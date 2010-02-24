from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^signup/$", "signup_codes.views.signup", name="test_signup"),
    url(r"^admin/invite_user/$", "signup_codes.views.admin_invite_user", name="admin_invite_user"),    
)