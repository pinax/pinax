# bbatest.py  --  Test Yahoo Mail API using BBauth
# Author: Jason Levitt
# Version 1.2, January 20th, 2007
#
# Tested with:
# Python 2.3.4 on Redhat Linux
# Apache 2.0.52/mod_python 3.2.10
#

#################################################
# User configurable data section                #
#################################################
# Put your Application ID and Secret here
APPID = '5KzQuKHIkxxxxxxxxxxxxxxxxxxSztLwiAF7'
SECRET = '0e68e582xxxxxxxxxxxxxxxxxxxx0f25f4'

##################################################
# End of user configurable data section          #
##################################################

from mod_python import apache
from mod_python import util
import urllib2
import ybrowserauth
from xml.sax import saxutils

# Possible parameter values sent by Yahoo! --
# ts: a timestamp
# sig: a caculated signature
# token: a token string
# userhash: a user hash
# appdata: user-defined application data

def handler(req):
    form = util.FieldStorage(req, keep_blank_values=1)
    ts = form.get("ts",None)
    sig = form.get("sig",None)
    token = form.get("token",None)
    userhash = form.get("userhash", None)
    appdata = form.get("appdata", None)

    # Instantiate the class    
    cptr = ybrowserauth.YBrowserAuth(APPID, SECRET, ts, sig, token, userhash, appdata)

    if token == None:
        # If no token is found, create the authentication URL and display it
        req.content_type = "text/html"
        outstuff = cptr.getAuthURL('someappdata', 1)
        req.send_http_header()
        req.write('<html><body><h1>Test Yahoo! Mail API Using BBauth</h1><h2>')
        req.write('<a href="' + outstuff + '">Click here to authorize access to your Y! Mail account</a>')
        req.write('</h2></body></html>')
    else:
        # If a token is found, it must be Yahoo!'s bbauth coming back as the
        # "success" URL. So, we validate the signature and do all the work
        req.content_type = "text/html"
        req.send_http_header()
        req.write('<html><body>')
        request_uri = req.parsed_uri[6]+ '?' + req.parsed_uri[7]
        cptr.validate_sig(ts, sig, request_uri)
        req.write('<h2>BBauth Login Successful</h2>')
        req.write('Userhash is: ' + cptr.userhash + '<br />')
        req.write('Appdata is: ' + cptr.appdata + '<br />')
        client = cptr.makeJSONRPCcall('ListFolders', [{}])
        req.write('Timeout is: ' + cptr.timeout + '<br />');
        req.write('WSSID is: ' + cptr.WSSID + '<br />');
        req.write('Cookie is: ' + cptr.cookie + '<br />');
        req.write('Token is: ' + cptr.token + '<br /><br />');
        req.write('Web Service call succeeded. Here are your mail folders: <br /><br /> ')
        for k in client['result']['folder']:
            if k['folderInfo']['name'] == '@B@Bulk':
                k['folderInfo']['name'] = 'Spam'
            req.write('<b>' + k['folderInfo']['name'] + ' </b> ' +  ' msgs: ' +  str(k['total']) +  ' unread: ' +  str(k['unread']) +  ' total bytes: ' +  str(k['size']) + '<br />')
        req.write('</body></html>')
    return apache.OK
