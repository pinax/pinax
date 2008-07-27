class OpenIDMiddleware(object):
    """
    Populate request.openid and request.openids with their openid. This comes 
    eithen from their cookie or from their session, depending on the presence 
    of OPENID_USE_SESSIONS.
    """
    def process_request(self, request):
        request.openids = request.session.get('openids', [])
        if request.openids:
            request.openid = request.openids[-1] # Last authenticated OpenID
        else:
            request.openid = None
