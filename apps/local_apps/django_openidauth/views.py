from django.shortcuts import render_to_response as render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as log_user_in, load_backend
from django.utils.html import escape
from django.conf import settings
from django.template import RequestContext

from django_openidauth.models import UserOpenID, associate_openid, unassociate_openid
from django_openidconsumer import views as consumer_views

import time, md5

def _make_hash(hash_type, user, openid):
    return md5.new('%s:%d:%s:%s' % (
        hash_type, user.id, str(openid), settings.SECRET_KEY
    )).hexdigest()

@login_required
def associations(request, template_name='openid_associations.html', post_login_redirect='/openid/complete/'):
    """
    A view for managing the OpenIDs associated with a user account.
    """
    if 'openid_url' in request.POST:
        # They entered a new OpenID and need to authenticate it - kick off the
        # process and make sure they are redirected back here afterwards
        return consumer_views.begin(request, redirect_to=post_login_redirect)
    
    messages = []
    associated_openids = [
        rec.openid
        for rec in UserOpenID.objects.filter(user__id = request.user.id)
    ]
    
    # OpenIDs are associated and de-associated based on their key - which is a
    # hash of the OpenID, user ID and SECRET_KEY - this gives us a nice key for
    # submit button names or checkbox values and provides CSRF protection at 
    # the same time. We need to pre-calculate the hashes for the user's OpenIDs
    # in advance.
    add_hashes = dict([
        (_make_hash('add', request.user, openid), str(openid))
        for openid in request.openids
        if str(openid) not in associated_openids
    ])
    del_hashes = dict([
        (_make_hash('del', request.user, openid), openid)
        for openid in associated_openids
    ])
    
    # We can now cycle through the keys in POST, looking for stuff to add or 
    # delete. First though we check for the ?direct=1 argument and directly add
    # any OpenIDs that were authenticated in the last 5 seconds - this supports
    # the case where a user has entered an OpenID in the form on this page, 
    # authenticated it and been directed straight back here.
    # TODO: Reconsider this technique now that it's easier to create custom 
    #       behaviour when an OpenID authentication is successful.
    if request.GET.get('direct') and request.openids and \
            request.openids[-1].issued > int(time.time()) - 5 and \
            str(request.openids[-1]) not in associated_openids:
        new_openid = str(request.openids[-1])
        associate_openid(request.user, new_openid)
        associated_openids.append(new_openid)
        messages.append('%s has been associated with your account' % escape(
            new_openid
        ))
    
    # Now cycle through POST.keys() looking for OpenIDs to add or remove
    for key in request.POST.keys():
        if key in add_hashes:
            openid = add_hashes[key]
            if openid not in associated_openids:
                associate_openid(request.user, openid)
                associated_openids.append(openid)
                messages.append('%s has been associated with your account' % \
                    escape(openid)
                )
        if key in del_hashes:
            openid = del_hashes[key]
            if openid in associated_openids:
                unassociate_openid(request.user, openid)
                associated_openids.remove(openid)
                messages.append('%s has been removed from your account' % \
                    escape(openid)
                )
    
    # At this point associated_openids represents the current set of associated
    # OpenIDs, and messages contains any messages that should be displayed. The
    # final step is to work out which OpenIDs they have that are currently 
    # logged in BUT are not associated - these are the ones that should be 
    # displayed with an "associate this?" buttons.
    potential_openids = [
        str(openid) for openid in request.openids
        if str(openid) not in associated_openids
    ]
    
    # Finally, calculate the button hashes we are going to need for the form.
    add_buttons = [
        {'openid': openid, 'hash': _make_hash('add', request.user, openid)}
        for openid in potential_openids
    ]
    del_buttons = [
        {'openid': openid, 'hash': _make_hash('del', request.user, openid)}
        for openid in associated_openids
    ]
    
    return render(template_name, {
        'user': request.user,
        'messages': messages,
        'action': request.path,
        'add_buttons': add_buttons,
        'del_buttons': del_buttons, # This is also used to generate the list of 
                                    # of associated OpenIDs
    },
    context_instance=RequestContext(request))

def complete(request, on_login_ok=None, on_login_failed=None, 
        on_login_ok_url=None, on_login_failed_url=None,
    ):
    """
    This view function takes optional arguments to configure how a successful
    or unsuccessful login will be dealt with. Default behaviour is to redirect
    to the homepage, appending a query string of loggedin=True or loggedin=False
    
    You can use the on_login_ok_url and on_login_failed_url arguments to 
    indicate different URLs for redirection after an OK or failed login attempt.
    
    Alternatively, you can provide your own view functions for these cases. For 
    example:
    
    def my_login_ok(request, identity_url):
        return HttpResponse(
            "Congratulations, you signed in as %s using OpenID %s" % (
                escape(request.user), escape(identity_url)
            ))
    
    def my_login_failed(request, identity_url):
        return HttpResponse(
            "Login failed; %s is not associated with an account" % (
                escape(identity_url)
            ))
    
    And in the URL configuration:
    
        (r'^openid/complete/$', 'django_openidauth.views.complete', {
            'on_login_ok': my_login_ok,
            'on_login_failed': my_login_failed,
        }),
    
    """
    if not on_login_ok:
        on_login_ok = lambda request, identity_url: HttpResponseRedirect(
            on_login_ok_url or '/?loggedin=True'
        )
    if not on_login_failed:
        on_login_failed = lambda request, identity_url: HttpResponseRedirect(
            on_login_failed_url or '/?loggedin=False'
        )
    
    def custom_on_success(request, identity_url, openid_response):
        # Reuse django_openidconsumer.views.default_on_success to set the 
        # relevant session variables:
        consumer_views.default_on_success(request, identity_url, openid_response)
        
        # Now look up the user's identity_url to see if they exist in the system
        try:
            user_openid = UserOpenID.objects.get(openid=identity_url)
        except UserOpenID.DoesNotExist:
            user_openid = None
        
        if user_openid:
            user = user_openid.user
            # Unfortunately we have to annotate the user with the 
            # 'django.contrib.auth.backends.ModelBackend' backend, or stuff breaks
            backend = load_backend('django.contrib.auth.backends.ModelBackend')
            user.backend = '%s.%s' % (
                backend.__module__, backend.__class__.__name__
            )
            log_user_in(request, user)
            
            return on_login_ok(request, identity_url)
        else:
            return on_login_failed(request, identity_url)
    
    # Re-use django_openidconsumer.views.complete, passing in a custom 
    # on_success function that checks to see if their OpenID is associated with 
    # a user in the system
    return consumer_views.complete(request, on_success=custom_on_success)
