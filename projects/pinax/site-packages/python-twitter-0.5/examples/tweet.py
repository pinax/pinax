#!/usr/bin/python

'''Post a message to twitter'''

__author__ = 'dewitt@google.com'

import ConfigParser
import getopt
import os
import sys
import twitter


USAGE = '''Usage: tweet [options] message

  This script posts a message to Twitter.

  Options:

    -h --help : print this help
    --username : the twitter username [optional]
    --password : the twitter password [optional]

  Documentation:

  If the --username or --password command line arguments are present they
  will be used to authenticate to Twitter.

  If either of the command line flags are not present, the environment
  variables TWEETUSERNAME and TWEETPASSWORD will then be checked for your
  username or password, respectively.

  If neither the command line flags nor the enviroment variables are
  present, the .tweetrc file, if it exists, can be used to set the
  default username and password.  The file should contain the
  following three lines, replacing *username* with your username, and
  *possword* with your password:

  A skeletal .tweetrc file:

    [Tweet]
    username: *username*
    password: *password*

'''

def PrintUsageAndExit():
  print USAGE
  sys.exit(2)

def GetUsernameEnv():
  return os.environ.get("TWEETUSERNAME", None)

def GetPasswordEnv():
  return os.environ.get("TWEETPASSWORD", None)

class TweetRc(object):
  def __init__(self):
    self._config = None

  def GetUsername(self):
    return self._GetOption('username')

  def GetPassword(self):
    return self._GetOption('password')

  def _GetOption(self, option):
    try:
      return self._GetConfig().get('Tweet', option)
    except:
      return None

  def _GetConfig(self):
    if not self._config:
      self._config = ConfigParser.ConfigParser()
      self._config.read(os.path.expanduser('~/.tweetrc'))
    return self._config

def main():
  try:
    shortflags = 'h'
    longflags = ['help', 'username=', 'password=', 'encoding=']
    opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)
  except getopt.GetoptError:
    PrintUsageAndExit()
  usernameflag = None
  passwordflag = None
  encoding = None
  for o, a in opts:
    if o in ("-h", "--help"):
      PrintUsageAndExit()
    if o in ("--username"):
      usernameflag = a
    if o in ("--password"):
      passwordflag = a
    if o in ("--encoding"):
      encoding = a
  message = ' '.join(args)
  if not message:
    PrintUsageAndExit()
  rc = TweetRc()
  username = usernameflag or GetUsernameEnv() or rc.GetUsername()
  password = passwordflag or GetPasswordEnv() or rc.GetPassword()
  if not username or not password:
    PrintUsageAndExit()
  api = twitter.Api(username=username, password=password, input_encoding=encoding)
  try:
    status = api.PostUpdate(message)
  except UnicodeDecodeError:
    print "Your message could not be encoded.  Perhaps it contains non-ASCII characters? "
    print "Try explicitly specifying the encoding with the  it with the --encoding flag"
    sys.exit(2)
  print "%s just posted: %s" % (status.user.name, status.text)

if __name__ == "__main__":
  main()
