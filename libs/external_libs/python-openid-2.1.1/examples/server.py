#!/usr/bin/env python

__copyright__ = 'Copyright 2005, Janrain, Inc.'

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse

import time
import Cookie
import cgi
import cgitb
import sys

def quoteattr(s):
    qs = cgi.escape(s, 1)
    return '"%s"' % (qs,)

try:
    import openid
except ImportError:
    sys.stderr.write("""
Failed to import the OpenID library. In order to use this example, you
must either install the library (see INSTALL in the root of the
distribution) or else add the library to python's import path (the
PYTHONPATH environment variable).

For more information, see the README in the root of the library
distribution or http://www.openidenabled.com/
""")
    sys.exit(1)

from openid.extensions import sreg
from openid.server import server
from openid.store.filestore import FileOpenIDStore
from openid.consumer import discover

class OpenIDHTTPServer(HTTPServer):
    """
    http server that contains a reference to an OpenID Server and
    knows its base URL.
    """
    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)

        if self.server_port != 80:
            self.base_url = ('http://%s:%s/' %
                             (self.server_name, self.server_port))
        else:
            self.base_url = 'http://%s/' % (self.server_name,)

        self.openid = None
        self.approved = {}
        self.lastCheckIDRequest = {}

    def setOpenIDServer(self, oidserver):
        self.openid = oidserver


class ServerHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.user = None
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)


    def do_GET(self):
        try:
            self.parsed_uri = urlparse(self.path)
            self.query = {}
            for k, v in cgi.parse_qsl(self.parsed_uri[4]):
                self.query[k] = v

            self.setUser()

            path = self.parsed_uri[2].lower()

            if path == '/':
                self.showMainPage()
            elif path == '/openidserver':
                self.serverEndPoint(self.query)

            elif path == '/login':
                self.showLoginPage('/', '/')
            elif path == '/loginsubmit':
                self.doLogin()
            elif path.startswith('/id/'):
                self.showIdPage(path)
            elif path.startswith('/yadis/'):
                self.showYadis(path[7:])
            elif path == '/serveryadis':
                self.showServerYadis()
            else:
                self.send_response(404)
                self.end_headers()

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(cgitb.html(sys.exc_info(), context=10))

    def do_POST(self):
        try:
            self.parsed_uri = urlparse(self.path)

            self.setUser()
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            self.query = {}
            for k, v in cgi.parse_qsl(post_data):
                self.query[k] = v

            path = self.parsed_uri[2]
            if path == '/openidserver':
                self.serverEndPoint(self.query)

            elif path == '/allow':
                self.handleAllow(self.query)
            else:
                self.send_response(404)
                self.end_headers()

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(cgitb.html(sys.exc_info(), context=10))

    def handleAllow(self, query):
        # pretend this next bit is keying off the user's session or something,
        # right?
        request = self.server.lastCheckIDRequest.get(self.user)

        if 'yes' in query:
            if 'login_as' in query:
                self.user = self.query['login_as']

            if request.idSelect():
                identity = self.server.base_url + 'id/' + query['identifier']
            else:
                identity = request.identity

            trust_root = request.trust_root
            if self.query.get('remember', 'no') == 'yes':
                self.server.approved[(identity, trust_root)] = 'always'

            response = self.approved(request, identity)

        elif 'no' in query:
            response = request.answer(False)

        else:
            assert False, 'strange allow post.  %r' % (query,)

        self.displayResponse(response)


    def setUser(self):
        cookies = self.headers.get('Cookie')
        if cookies:
            morsel = Cookie.BaseCookie(cookies).get('user')
            if morsel:
                self.user = morsel.value

    def isAuthorized(self, identity_url, trust_root):
        if self.user is None:
            return False

        if identity_url != self.server.base_url + 'id/' + self.user:
            return False

        key = (identity_url, trust_root)
        return self.server.approved.get(key) is not None

    def serverEndPoint(self, query):
        try:
            request = self.server.openid.decodeRequest(query)
        except server.ProtocolError, why:
            self.displayResponse(why)
            return

        if request is None:
            # Display text indicating that this is an endpoint.
            self.showAboutPage()
            return

        if request.mode in ["checkid_immediate", "checkid_setup"]:
            self.handleCheckIDRequest(request)
        else:
            response = self.server.openid.handleRequest(request)
            self.displayResponse(response)

    def addSRegResponse(self, request, response):
        sreg_req = sreg.SRegRequest.fromOpenIDRequest(request)

        # In a real application, this data would be user-specific,
        # and the user should be asked for permission to release
        # it.
        sreg_data = {
            'nickname':self.user
            }

        sreg_resp = sreg.SRegResponse.extractResponse(sreg_req, sreg_data)
        response.addExtension(sreg_resp)

    def approved(self, request, identifier=None):
        response = request.answer(True, identity=identifier)
        self.addSRegResponse(request, response)
        return response

    def handleCheckIDRequest(self, request):
        is_authorized = self.isAuthorized(request.identity, request.trust_root)
        if is_authorized:
            response = self.approved(request)
            self.displayResponse(response)
        elif request.immediate:
            response = request.answer(False)
            self.displayResponse(response)
        else:
            self.server.lastCheckIDRequest[self.user] = request
            self.showDecidePage(request)

    def displayResponse(self, response):
        try:
            webresponse = self.server.openid.encodeResponse(response)
        except server.EncodingError, why:
            text = why.response.encodeToKVForm()
            self.showErrorPage('<pre>%s</pre>' % cgi.escape(text))
            return

        self.send_response(webresponse.code)
        for header, value in webresponse.headers.iteritems():
            self.send_header(header, value)
        self.writeUserHeader()
        self.end_headers()

        if webresponse.body:
            self.wfile.write(webresponse.body)

    def doLogin(self):
        if 'submit' in self.query:
            if 'user' in self.query:
                self.user = self.query['user']
            else:
                self.user = None
            self.redirect(self.query['success_to'])
        elif 'cancel' in self.query:
            self.redirect(self.query['fail_to'])
        else:
            assert 0, 'strange login %r' % (self.query,)

    def redirect(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.writeUserHeader()

        self.end_headers()

    def writeUserHeader(self):
        if self.user is None:
            t1970 = time.gmtime(0)
            expires = time.strftime(
                'Expires=%a, %d-%b-%y %H:%M:%S GMT', t1970)
            self.send_header('Set-Cookie', 'user=;%s' % expires)
        else:
            self.send_header('Set-Cookie', 'user=%s' % self.user)

    def showAboutPage(self):
        endpoint_url = self.server.base_url + 'openidserver'

        def link(url):
            url_attr = quoteattr(url)
            url_text = cgi.escape(url)
            return '<a href=%s><code>%s</code></a>' % (url_attr, url_text)

        def term(url, text):
            return '<dt>%s</dt><dd>%s</dd>' % (link(url), text)

        resources = [
            (self.server.base_url, "This example server's home page"),
            ('http://www.openidenabled.com/',
             'An OpenID community Web site, home of this library'),
            ('http://www.openid.net/', 'the official OpenID Web site'),
            ]

        resource_markup = ''.join([term(url, text) for url, text in resources])

        self.showPage(200, 'This is an OpenID server', msg="""\
        <p>%s is an OpenID server endpoint.<p>
        <p>For more information about OpenID, see:</p>
        <dl>
        %s
        </dl>
        """ % (link(endpoint_url), resource_markup,))

    def showErrorPage(self, error_message):
        self.showPage(400, 'Error Processing Request', err='''\
        <p>%s</p>
        <!--

        This is a large comment.  It exists to make this page larger.
        That is unfortunately necessary because of the "smart"
        handling of pages returned with an error code in IE.

        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************
        *************************************************************

        -->
        ''' % error_message)

    def showDecidePage(self, request):
        id_url_base = self.server.base_url+'id/'
        # XXX: This may break if there are any synonyms for id_url_base,
        # such as referring to it by IP address or a CNAME.
        assert request.identity.startswith(id_url_base), repr((request.identity, id_url_base))
        expected_user = request.identity[len(id_url_base):]

        if request.idSelect(): # We are being asked to select an ID
            msg = '''\
            <p>A site has asked for your identity.  You may select an
            identifier by which you would like this site to know you.
            On a production site this would likely be a drop down list
            of pre-created accounts or have the facility to generate
            a random anonymous identifier.
            </p>
            '''
            fdata = {
                'id_url_base': id_url_base,
                'trust_root': request.trust_root,
                }
            form = '''\
            <form method="POST" action="/allow">
            <table>
              <tr><td>Identity:</td>
                 <td>%(id_url_base)s<input type='text' name='identifier'></td></tr>
              <tr><td>Trust Root:</td><td>%(trust_root)s</td></tr>
            </table>
            <p>Allow this authentication to proceed?</p>
            <input type="checkbox" id="remember" name="remember" value="yes"
                /><label for="remember">Remember this
                decision</label><br />
            <input type="submit" name="yes" value="yes" />
            <input type="submit" name="no" value="no" />
            </form>
            '''%fdata
        elif expected_user == self.user:
            msg = '''\
            <p>A new site has asked to confirm your identity.  If you
            approve, the site represented by the trust root below will
            be told that you control identity URL listed below. (If
            you are using a delegated identity, the site will take
            care of reversing the delegation on its own.)</p>'''

            fdata = {
                'identity': request.identity,
                'trust_root': request.trust_root,
                }
            form = '''\
            <table>
              <tr><td>Identity:</td><td>%(identity)s</td></tr>
              <tr><td>Trust Root:</td><td>%(trust_root)s</td></tr>
            </table>
            <p>Allow this authentication to proceed?</p>
            <form method="POST" action="/allow">
              <input type="checkbox" id="remember" name="remember" value="yes"
                  /><label for="remember">Remember this
                  decision</label><br />
              <input type="submit" name="yes" value="yes" />
              <input type="submit" name="no" value="no" />
            </form>''' % fdata
        else:
            mdata = {
                'expected_user': expected_user,
                'user': self.user,
                }
            msg = '''\
            <p>A site has asked for an identity belonging to
            %(expected_user)s, but you are logged in as %(user)s.  To
            log in as %(expected_user)s and approve the login request,
            hit OK below.  The "Remember this decision" checkbox
            applies only to the trust root decision.</p>''' % mdata

            fdata = {
                'identity': request.identity,
                'trust_root': request.trust_root,
                'expected_user': expected_user,
                }
            form = '''\
            <table>
              <tr><td>Identity:</td><td>%(identity)s</td></tr>
              <tr><td>Trust Root:</td><td>%(trust_root)s</td></tr>
            </table>
            <p>Allow this authentication to proceed?</p>
            <form method="POST" action="/allow">
              <input type="checkbox" id="remember" name="remember" value="yes"
                  /><label for="remember">Remember this
                  decision</label><br />
              <input type="hidden" name="login_as" value="%(expected_user)s"/>
              <input type="submit" name="yes" value="yes" />
              <input type="submit" name="no" value="no" />
            </form>''' % fdata

        self.showPage(200, 'Approve OpenID request?', msg=msg, form=form)

    def showIdPage(self, path):
        link_tag = '<link rel="openid.server" href="%sopenidserver">' %\
              self.server.base_url
        yadis_loc_tag = '<meta http-equiv="x-xrds-location" content="%s">'%\
            (self.server.base_url+'yadis/'+path[4:])
        disco_tags = link_tag + yadis_loc_tag
        ident = self.server.base_url + path[1:]

        approved_trust_roots = []
        for (aident, trust_root) in self.server.approved.keys():
            if aident == ident:
                trs = '<li><tt>%s</tt></li>\n' % cgi.escape(trust_root)
                approved_trust_roots.append(trs)

        if approved_trust_roots:
            prepend = '<p>Approved trust roots:</p>\n<ul>\n'
            approved_trust_roots.insert(0, prepend)
            approved_trust_roots.append('</ul>\n')
            msg = ''.join(approved_trust_roots)
        else:
            msg = ''

        self.showPage(200, 'An Identity Page', head_extras=disco_tags, msg='''\
        <p>This is an identity page for %s.</p>
        %s
        ''' % (ident, msg))

    def showYadis(self, user):
        self.send_response(200)
        self.send_header('Content-type', 'application/xrds+xml')
        self.end_headers()

        endpoint_url = self.server.base_url + 'openidserver'
        user_url = self.server.base_url + 'id/' + user
        self.wfile.write("""\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type>%s</Type>
      <Type>%s</Type>
      <URI>%s</URI>
      <LocalID>%s</LocalID>
    </Service>

  </XRD>
</xrds:XRDS>
"""%(discover.OPENID_2_0_TYPE, discover.OPENID_1_0_TYPE,
     endpoint_url, user_url))

    def showServerYadis(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/xrds+xml')
        self.end_headers()

        endpoint_url = self.server.base_url + 'openidserver'
        self.wfile.write("""\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type>%s</Type>
      <URI>%s</URI>
    </Service>

  </XRD>
</xrds:XRDS>
"""%(discover.OPENID_IDP_2_0_TYPE, endpoint_url,))

    def showMainPage(self):
        yadis_tag = '<meta http-equiv="x-xrds-location" content="%s">'%\
            (self.server.base_url + 'serveryadis')
        if self.user:
            openid_url = self.server.base_url + 'id/' + self.user
            user_message = """\
            <p>You are logged in as %s. Your OpenID identity URL is
            <tt><a href=%s>%s</a></tt>. Enter that URL at an OpenID
            consumer to test this server.</p>
            """ % (self.user, quoteattr(openid_url), openid_url)
        else:
            user_message = """\
            <p>This server uses a cookie to remember who you are in
            order to simulate a standard Web user experience. You are
            not <a href='/login'>logged in</a>.</p>"""

        self.showPage(200, 'Main Page', head_extras = yadis_tag, msg='''\
        <p>This is a simple OpenID server implemented using the <a
        href="http://openid.schtuff.com/">Python OpenID
        library</a>.</p>

        %s

        <p>To use this server with a consumer, the consumer must be
        able to fetch HTTP pages from this web server. If this
        computer is behind a firewall, you will not be able to use
        OpenID consumers outside of the firewall with it.</p>

        <p>The URL for this server is <a href=%s><tt>%s</tt></a>.</p>
        ''' % (user_message, quoteattr(self.server.base_url), self.server.base_url))

    def showLoginPage(self, success_to, fail_to):
        self.showPage(200, 'Login Page', form='''\
        <h2>Login</h2>
        <p>You may log in with any name. This server does not use
        passwords because it is just a sample of how to use the OpenID
        library.</p>
        <form method="GET" action="/loginsubmit">
          <input type="hidden" name="success_to" value="%s" />
          <input type="hidden" name="fail_to" value="%s" />
          <input type="text" name="user" value="" />
          <input type="submit" name="submit" value="Log In" />
          <input type="submit" name="cancel" value="Cancel" />
        </form>
        ''' % (success_to, fail_to))

    def showPage(self, response_code, title,
                 head_extras='', msg=None, err=None, form=None):

        if self.user is None:
            user_link = '<a href="/login">not logged in</a>.'
        else:
            user_link = 'logged in as <a href="/id/%s">%s</a>.<br /><a href="/loginsubmit?submit=true&success_to=/login">Log out</a>' % \
                        (self.user, self.user)

        body = ''

        if err is not None:
            body +=  '''\
            <div class="error">
              %s
            </div>
            ''' % err

        if msg is not None:
            body += '''\
            <div class="message">
              %s
            </div>
            ''' % msg

        if form is not None:
            body += '''\
            <div class="form">
              %s
            </div>
            ''' % form

        contents = {
            'title': 'Python OpenID Server Example - ' + title,
            'head_extras': head_extras,
            'body': body,
            'user_link': user_link,
            }

        self.send_response(response_code)
        self.writeUserHeader()
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write('''<html>
  <head>
    <title>%(title)s</title>
    %(head_extras)s
  </head>
  <style type="text/css">
      h1 a:link {
          color: black;
          text-decoration: none;
      }
      h1 a:visited {
          color: black;
          text-decoration: none;
      }
      h1 a:hover {
          text-decoration: underline;
      }
      body {
        font-family: verdana,sans-serif;
        width: 50em;
        margin: 1em;
      }
      div {
        padding: .5em;
      }
      table {
        margin: none;
        padding: none;
      }
      .banner {
        padding: none 1em 1em 1em;
        width: 100%%;
      }
      .leftbanner {
        text-align: left;
      }
      .rightbanner {
        text-align: right;
        font-size: smaller;
      }
      .error {
        border: 1px solid #ff0000;
        background: #ffaaaa;
        margin: .5em;
      }
      .message {
        border: 1px solid #2233ff;
        background: #eeeeff;
        margin: .5em;
      }
      .form {
        border: 1px solid #777777;
        background: #ddddcc;
        margin: .5em;
        margin-top: 1em;
        padding-bottom: 0em;
      }
      dd {
        margin-bottom: 0.5em;
      }
  </style>
  <body>
    <table class="banner">
      <tr>
        <td class="leftbanner">
          <h1><a href="/">Python OpenID Server Example</a></h1>
        </td>
        <td class="rightbanner">
          You are %(user_link)s
        </td>
      </tr>
    </table>
%(body)s
  </body>
</html>
''' % contents)


def main(host, port, data_path):
    addr = (host, port)
    httpserver = OpenIDHTTPServer(addr, ServerHandler)

    # Instantiate OpenID consumer store and OpenID consumer.  If you
    # were connecting to a database, you would create the database
    # connection and instantiate an appropriate store here.
    store = FileOpenIDStore(data_path)
    oidserver = server.Server(store, httpserver.base_url + 'openidserver')

    httpserver.setOpenIDServer(oidserver)

    print 'Server running at:'
    print httpserver.base_url
    httpserver.serve_forever()

if __name__ == '__main__':
    host = 'localhost'
    data_path = 'sstore'
    port = 8000

    try:
        import optparse
    except ImportError:
        pass # Use defaults (for Python 2.2)
    else:
        parser = optparse.OptionParser('Usage:\n %prog [options]')
        parser.add_option(
            '-d', '--data-path', dest='data_path', default=data_path,
            help='Data directory for storing OpenID consumer state. '
            'Defaults to "%default" in the current directory.')
        parser.add_option(
            '-p', '--port', dest='port', type='int', default=port,
            help='Port on which to listen for HTTP requests. '
            'Defaults to port %default.')
        parser.add_option(
            '-s', '--host', dest='host', default=host,
            help='Host on which to listen for HTTP requests. '
            'Also used for generating URLs. Defaults to %default.')

        options, args = parser.parse_args()
        if args:
            parser.error('Expected no arguments. Got %r' % args)

        host = options.host
        port = options.port
        data_path = options.data_path

    main(host, port, data_path)
