# ybrowserauth.py  --  A class for accessing Yahoo! Mail and Photos using BBauth
# Author: Jason Levitt
# Version 1.2, January 20th, 2007
#
# Tested with:
# Python 2.3.4 on Redhat Linux
# Apache 2.0.52/mod_python 3.2.10
#

__revision__ = '$Revision: 000 $'

import re
import urlparse
import urllib2
from urllib import urlencode
import md5
from time import time
import simplejson

# Various exceptions

class JSONrpcError (Exception):
    "Class that handles exceptions raised during access credentials processing"
    def __init__(self, code, json):
        self.returnedStuff = code + " JSON: " + json
    def __str__(self):
        return str(self.returnedStuff)

#JSONrpcErrorCode - raised when a 500 status is returned
# by a JSONRPC call
class JSONrpcErrorCode(JSONrpcError):
    "Exception class called when an ErrorCode is returned in XML response for access credentials"
    pass    
    
class WebServiceCallError(Exception):
    "Exception class for web service related errors"
    def __init__(self, arg = None):
        self.val = arg
    def __str__(self):
        return str(self.val)

# WSxmlErrorCode - raised when an ErrorCode is returned in the XML
# from a request for access credentials
class WSxmlErrorCode(WebServiceCallError):
    "Exception class called when an ErrorCode is returned in XML response for access credentials"
    pass
# WShttpError - raised when an HTTP error is returned when making an
# authenticated web service call or when fetching access credentials
class WShttpError(WebServiceCallError):
    "Raised when an HTTP error is returned when making an authenticated web service call or when fetching access credentials"
    pass
# WSurlError - raised when a network error is returned when making an
# authenticated web service call or when fetching access credentials
class WSurlError(WebServiceCallError):
    "Raised when a network error is returned when making an authenticated web service call or when fetching access credentials"
    pass
# WSunknownError - raised when an unknown error occurs when making an
# authenticated web service call or when fetching access credentials
class WSunknownError(WebServiceCallError):
    "Raised when an unknown error occurs when making an authenticated web service call or when fetching access credentials"
    pass

class CredentialsError(Exception):
    "Class that handles exceptions raised during access credentials processing"
    def __init__(self, xml = None):
        self.returnedXml = xml
    def __str__(self):
        return str(self.returnedXml)

# MissingCookie - raised when the Cookie was not returned
# from an access credentials request
class MissingCookie(CredentialsError):
    "Exception raised when cookie is missing from access credentials response"
    pass
# MissingWSSID - raised when the WSSID was not returned
# from an access credentials request
class MissingWSSID(CredentialsError):
    "Exception raised when WSSID is missing from access credentials response"
    pass
# MissingTimeout - raised when the Timeout was not returned
# from an access credentials request
class MissingTimeout(CredentialsError):
    "Exception raised when timeout is missing from access credentials response"
    pass

class SigValidationError(Exception):
    "Class used to raise exception when signature is not validated"
    def __init__(self, data = None):
        self.sigstuff = data
    def __str__(self):
        return str(self.sigstuff)

# NoSigFoundError -  raised when no signature is found in the
# REQUEST_URI
class NoSigFoundError(SigValidationError):
    "Class used to raise exception when no signature is found in the REQUEST_URI"
    pass
# SigDoesNotMatchError - raised when the requesting signature does
# not match the computed signature
class SigDoesNotMatchError(SigValidationError):
    "Raised when the requesting signature does not match the computed signature"
    pass
# InvalidSigUrlError - raised when the signature found in the
# REQUEST_URI is, for some reason, invalid
class InvalidSigUrlError(SigValidationError):
    "Raised when the signature found in the REQUEST_URI is, for some reason, invalid"
    pass
# InvalidTimestamp - raised when the timestamp is too far off
# from the allowed delay between requesting authentication and
# computing the validity of the authentication. Usually, this is
# some amount greater than 10 minutes or so.
class InvalidTimestamp(SigValidationError):
    "Raised when the timestamp is too far off from the allowed delay between requesting authentication and computing the validity of the authentication. Usually, this is some amount greater than 10 minutes or so."
    pass
# SigCalcError - raised when an error occured when trying to calculate
# the signature
class SigCalcError(SigValidationError):
    "Raised when an error occured when trying to calculate the signature"
    pass


class YBrowserAuth:
    "Yahoo! Browser-Based Authentication for Python"
    
    WSLOGIN_PREFIX = 'https://api.login.yahoo.com/WSLogin/V1/'
    JSON_RPC_ENDPOINT = 'http://mail.yahooapis.com/ws/mail/v1.1/jsonrpc'


    def __init__(self, yourappid, yoursecret, envts=None, envsig=None, envtoken=None, envuserhash=None, envappdata=None):
        self.appid = yourappid
        self.secret = yoursecret
        self.ts = envts
        self.sig = envsig
        self.timeout = ''
        self.token = envtoken
        self.WSSID = ''
        self.cookie = ''
        self.userhash = envuserhash
        self.appdata = envappdata

    def createAuthURL(self, aurl):
        """
        Private utility method for creating an authenticated URL
    
        Arguments:
            - aurl, a URL needing authentication data
        Return:
            - a string that is a URL with auth data appended
        """
        parts = urlparse.urlparse(aurl)
        tstamp = str(int(time()))
        relative_uri = ""
        if parts[2] != "":
            relative_uri = parts[2]
        if parts[4] == "":
            relative_uri = relative_uri + '?ts=' + tstamp
        else:
            relative_uri = relative_uri + '?' + parts[4] + '&ts=' + tstamp
        self.sig = md5.new(relative_uri + self.secret).hexdigest()
        signed_url = parts[0] +  '://' + parts[1] + relative_uri + '&sig=' + self.sig
        return signed_url        
        
    def getAuthURL(self, appd=None, uhash=1):
        """
        Creates the intial authenticated URL used for Browser-Based auth
        
        Arguments:
            - appd (optional), any data string you want saved and sent back from Yahoo! upon
                    successful user authentication
            - uhash (optional), a boolean indicating whether you want Yahoo! to return
                    the user hash upon successful user authentication
        Return:
            - a string that is a URL with auth data appended
        """
        if appd != "" and appd != None:
            appdata = '&' + urlencode({'appdata':appd})
        else:
            appdata = ''
        if uhash != "" and uhash != None:
            hashdata = '&send_userhash=1'
        else:
            hashdata = ''
        return self.createAuthURL(YBrowserAuth.WSLOGIN_PREFIX + 'wslogin?appid=' + self.appid + appdata + hashdata)
    
    def getAccessURL(self):
        """
        Creates URL used to retrieve Web Service access credentials from Yahoo!
        
        Arguments:
           NONE
           
        Return:
            - a string that is a URL with auth data appended
        """
        return self.createAuthURL(YBrowserAuth.WSLOGIN_PREFIX + 'wspwtoken_login?token=' + self.token + '&appid=' + self.appid)

    def getAccessCredentials(self):
        """
        Private function used to retrieve web service access credentials
        
        Arguments:
            NONE
        Return:
            NONE
        """
        url = self.getAccessURL()
        
        try:
            xml = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            raise WShttpError("HTTP error: %d" % e.code)
        except urllib2.URLError, e:
            raise WSurlError("Network error: %s" % e.reason.args[1])
        except:
            raise WSunknownError("Unknown error on credentials web service call. Url = " + url)

        xmlsrch = re.search('<ErrorCode>(.+)</ErrorCode>', xml)
        
        if xmlsrch != None:
            raise WSxmlErrorCode(xml)
        
        xmlsrch = re.search('(Y=.*)', xml)
        
        if xmlsrch == None:
            raise MissingCookie(xml)
        self.cookie = xmlsrch.group(1)

        xmlsrch = re.search('<WSSID>(.+)</WSSID>', xml)
        
        if xmlsrch == None:
            raise MissingWSSID(xml)
        self.WSSID = xmlsrch.group(1)

        xmlsrch = re.search('<Timeout>(.+)</Timeout>', xml)
        
        if xmlsrch == None:
            raise MissingTimeout(xml)
        self.timeout = xmlsrch.group(1)

        return

    def createAuthWSurl(self, wurl):
        """
        Build a URL specifically for making authenticated web service calls
        
        Arguments:
            - wurl the web service call URL
        Return:
            - the same URL with authentication data appended
        """
        if self.cookie == '':
                self.getAccessCredentials()
                
        wurl = wurl.strip()
        if not('?' in wurl):
            wurl = wurl + '?'

        return wurl + '&WSSID=' + self.WSSID + '&appid='  + self.appid

    def validate_sig(self, tstamp, ysig, relative_url):
        """
        Validates the signature returned by a Yahoo! login
        
        Arguments:
            - tstamp the timestamp sent by Yahoo!
            - ysig the signature sent by Yahoo!
            - relative_url the REQUEST_URI 
        Return:
            NONE
        """
        if tstamp:
            self.ts = tstamp
        if ysig:
            self.sig = ysig

        sig_search = re.search('^(.+)&sig=(\w{32})$', relative_url)

        if sig_search != None:
            relative_url_without_sig = sig_search.group(1)
            try:
                passed_sig = sig_search.group(2)
            except:
                raise  NoSigFoundError("No signature found in url. Url = " + relative_url)
            if passed_sig != self.sig:
                raise  SigDoesNotMatchError("Invalid sig may have been passed. Passed sig is " + passed_sig)
        else:
            raise InvalidSigUrlError("Invalid url may have been passed - relative_url: " + relative_url)

        current_time = int(time())
        clock_skew  = abs(current_time - int(self.ts))
        if clock_skew > 600:
            raise InvalidTimestamp("Invalid timestamp - clock_skew is: " + str(clock_skew) + " seconds, current time is: " + str(current_time) + ", ts is: " + self.ts)

        sig_input = relative_url_without_sig + self.secret
        calculated_sig = md5.new(sig_input).hexdigest()
        if calculated_sig != self.sig:
            raise SigCalcError("calculated_sig was: " + calculated_sig + ", supplied sig was: " + self.sig + ", sig input was: " + sig_input)

        return
    
    def makeAuthWSgetCall(self, url):
        """
        Make an authenticated web service call
        
        Arguments:
            - url the non-authenticated REST call you want to make
        Return:
            - string, the XML/JSON/PHP response from the web service request
        """
        url = self.createAuthWSurl(url)
        
        request = urllib2.Request(url)
        request.add_header('Cookie', self.cookie)

        try:
            xml = urllib2.urlopen(request).read()
        except urllib2.HTTPError, e:
            raise WShttpError("HTTP error: %d" % e.code)
        except urllib2.URLError, e:
            raise WSurlError("Network error: %s" % e.reason.args[1])
        except:
            raise WSunknownError("Unknown error on auth web service call. Url = " + url)            
        
        return xml

    def makeJSONRPCcall(self, method, params):
        """
        Make an authenticated web service call
        
        Arguments:
            - method a string that is the Mail API method name you wish to invoke
            - params a Pythond dict object that is the JSON parameters for the method
        Return:
            - Python dict object, the decoded JSON response from the web service request
        """
        self.getAccessCredentials()
        
        thecall = {}
        thecall["method"] = method
        thecall["params"] = params
        
        data = simplejson.dumps(thecall)

        request = urllib2.Request(YBrowserAuth.JSON_RPC_ENDPOINT + '?appid=' + self.appid + '&WSSID=' + self.WSSID, data)
        request.add_header('Cookie', self.cookie)
        request.add_header('Content-Type', 'application/json')

        try:
            json = urllib2.urlopen(request).read()
        except urllib2.HTTPError, e:
            raise JSONrpcErrorCode("HTTP error: %d" % e.code, json='[nothing returned]')
        except urllib2.URLError, e:
            raise WSurlError("Network error: %s" % e.reason.args[1])
        except:
            raise WSunknownError("Unknown error on auth web service call. Url = " + YBrowserAuth.JSON_RPC_ENDPOINT)            

        python_obj = simplejson.loads(json)

        return python_obj    
