from turbogears import testutil
from genshitest.controllers import Root
import cherrypy

cherrypy.root = Root()

def test_method():
    "the index method should return a string called now"
    import types
    result = testutil.call(cherrypy.root.index)
    assert type(result["now"]) == types.StringType

def test_indextitle():
    "The mainpage should have the right title"
    testutil.createRequest("/")
    assert "<TITLE>Welcome to TurboGears</TITLE>" in cherrypy.response.body[0]
