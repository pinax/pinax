import cherrypy

def is_xhr():
    requested_with = cherrypy.request.headers.get('X-Requested-With')
    return requested_with and requested_with.lower() == 'xmlhttprequest'
