# bbatest.py  --  Test Yahoo! Photos web services using BBauth
# Author: Jason Levitt
# Version 1.2, March 19th, 2007
#
# Tested with:
# Python 2.3.4 on Redhat Linux
# Apache 2.0.52/mod_python 3.2.10
#

#################################################
# User configurable data section                #
#################################################
# Put your Application ID and Secret here
APPID = 'DMcB2PTIxxxxxxxxxxxxxxxx5fN69UmnCU-'
SECRET = '6589ebbxxxxxxxxxxxxxxxxx14e92037'

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
        req.write('<html><body><h1>Test Yahoo! Photos Web Services Using BBauth</h1><h2>')
        req.write('<a href="' + outstuff + '">Click here to authorize access to your Y! Photos account</a>')
        req.write('</h2></body></html>')
    else:
        # If a token is found, it must be Yahoo!'s bbauth coming back as the
        # "success" URL. So, we validate the signature and do all the work
        req.content_type = "text/html"
        req.send_http_header()
        req.write('<html><body>')
        request_uri = req.parsed_uri[6]+ '?' + req.parsed_uri[7]
        cptr.validate_sig(ts, sig, request_uri)
        req.write('<h2>BBauth login successful</h2>')
        req.write('Userhash is: ' + cptr.userhash + '<br />')
        req.write('Appdata is: ' + cptr.appdata + '<br />')
        xml = cptr.makeAuthWSgetCall('http://photos.yahooapis.com/V3.0/listAlbums?')
        req.write('Timeout is: ' + cptr.timeout + '<br />');
        req.write('WSSID is: ' + cptr.WSSID + '<br />');
        req.write('Cookie is: ' + cptr.cookie + '<br />');
        req.write('Token is: ' + cptr.token + '<br /><br />');
        req.write('Web Service call succeeded. XML response is: <br /><br /> ' + saxutils.escape(xml))
        req.write('</body></html>')
    return apache.OK
