import logging

import cherrypy

import turbogears
from turbogears import controllers, expose, validate, redirect, widgets
from turbogears import identity

from genshitest import json

log = logging.getLogger("genshitest.controllers")

class Root(controllers.RootController):

    @expose(template="genshitest.templates.welcome")
    def index(self):
        import time
        log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime(),
                    widget=widgets.TextArea(name="widget_test",
                                            default="Lorem ipsum",
                                            rows=5, cols=40))

    @expose(template="genshi-text:genshitest.templates.plain",
            content_type='text/plain; charset=utf-8')
    def plain(self):
        return dict(name='world')

    @expose(template="genshitest.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= cherrypy.request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= cherrypy.request.headers.get("Referer", "/")
        cherrypy.response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")
