# -*- coding: utf-8 -*-
"""
 Copyright (c) 2007, Benoît Chesneau
 Copyright (c) 2007, Simon Willison, original work on django-openid

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
     * Neither the name of the <ORGANIZATION> nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


from django.http import HttpResponse, HttpResponseRedirect, get_host
from django.shortcuts import get_object_or_404, render_to_response as render
from django.template import RequestContext, loader, Context
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.utils.encoding import smart_str
from django.utils.http import urlquote_plus, urlquote

from openid.consumer.consumer import Consumer, \
    SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg
# needed for some linux distributions like debian
try:
    from openid.yadis import xri
except:
    from yadis import xri

import md5, re, time, urllib


from util import OpenID, DjangoOpenIDStore, from_openid_response
from models import UserAssociation, UserPasswordQueue
from forms import OpenidSigninForm, OpenidAuthForm, OpenidRegisterForm, \
        OpenidVerifyForm, RegistrationForm, ChangepwForm, ChangeemailForm, \
        ChangeopenidForm, DeleteForm, EmailPasswordForm

from decorators import username_control

def get_url_host(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(get_host(request))
    return '%s://%s' % (protocol, host)

def get_full_url(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(request.META['HTTP_HOST'])
    return get_url_host(request) + request.get_full_path()

next_url_re = re.compile('^/[-\w/]+$')

def is_valid_next_url(next):
    # When we allow this:
    #   /openid/?next=/welcome/
    # For security reasons we want to restrict the next= bit to being a local 
    # path, not a complete URL.
    return bool(next_url_re.match(next))

def ask_openid(request, openid_url, redirect_to, on_failure=None, sreg_request=None):
    """ basic function to ask openid and return response """

    on_failure = on_failure or signin_failure
    
    trust_root = getattr(
        settings, 'OPENID_TRUST_ROOT', get_url_host(request) + '/'
    )
    if xri.identifierScheme(openid_url) == 'XRI' and getattr(
            settings, 'OPENID_DISALLOW_INAMES', False
    ):
        msg = _("i-names are not supported")
        return on_failure(request,msg)
    consumer = Consumer(request.session, DjangoOpenIDStore())
    try:
        auth_request = consumer.begin(openid_url)
    except DiscoveryFailure:
        msg =_("The OpenID %s was invalid" % openid_url)
        return on_failure(request,msg)

    auth_request.addExtension(sreg_request)
    redirect_url = auth_request.redirectURL(trust_root, redirect_to)
    return HttpResponseRedirect(redirect_url)

def complete(request, on_success=None, on_failure=None, return_to=None):
    on_success = on_success or default_on_success
    on_failure = on_failure or default_on_failure
    
    consumer = Consumer(request.session, DjangoOpenIDStore())
    openid_response = consumer.complete(dict(request.GET.items()), return_to)
    
    if openid_response.status == SUCCESS:
        return on_success(request, openid_response.identity_url, openid_response)
    elif openid_response.status == CANCEL:
        return on_failure(request, 'The request was cancelled')
    elif openid_response.status == FAILURE:
        return on_failure(request, openid_response.message)
    elif openid_response.status == SETUP_NEEDED:
        return on_failure(request, 'Setup needed')
    else:
        assert False, "Bad openid status: %s" % openid_response.status

def default_on_success(request, identity_url, openid_response):
    request.session['openid']=from_openid_response(openid_response)
    
    next = request.GET.get('next', '').strip()
    if not next or not is_valid_next_url(next):
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
    
    return HttpResponseRedirect(next)

def default_on_failure(request, message):
    return render('openid_failure.html', {
        'message': message
    })


def signin(request):
    """
    signin page. It manage the legacy authentification (user/password) 
    and authentification with openid.

    url: /signin/
    
    template : authopenid/signin.htm
    """

    on_failure = signin_failure
    next = ''


    if request.GET.get('next') and is_valid_next_url(request.GET['next']):
        next = request.GET.get('next', '').strip()
    if not next or not is_valid_next_url(next):
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')

    if request.user.is_authenticated():
        return HttpResponseRedirect(next)


    form_signin = OpenidSigninForm(initial={'next':next})
    form_auth = OpenidAuthForm(initial={'next':next})

    if request.POST:   
        if 'bsignin' in request.POST.keys():
            form_signin = OpenidSigninForm(request.POST)
            if form_signin.is_valid():
                next = form_signin.cleaned_data['next']
                if not next:
                    next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')

                sreg_req = sreg.SRegRequest(optional=['nickname','email'])
                redirect_to = "%s?%s" % (
                        get_url_host(request) + reverse('user_complete_signin'), 
                        urllib.urlencode({'next':next}))

                return ask_openid(request, 
                        form_signin.cleaned_data['openid_url'], 
                        redirect_to, 
                        on_failure=signin_failure, 
                        sreg_request=sreg_req)

        elif 'blogin' in request.POST.keys():
            # perform normal django authentification
            form_auth = OpenidAuthForm(request.POST)
            if form_auth.is_valid():
                u = form_auth.get_user()
                login(request, u)

                next = form_auth.cleaned_data['next']
                if not next:
                    next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
                return HttpResponseRedirect(next)


    return render('authopenid/signin.html', {
        'form1': form_auth,
        'form2': form_signin,
        'action': request.path,
        'msg':  request.GET.get('msg',''),
        'sendpw_url': reverse('user_sendpw'),
    }, context_instance=RequestContext(request))

def complete_signin(request):
    """ in case of complete signin with openid """
    return complete(request, signin_success, signin_failure, get_url_host(request) + reverse('user_complete_signin'))


def signin_success(request, identity_url, openid_response):
    """
    openid signin success.

    If the openid is already registered, the user is redirected to 
    url set par next or in settings with OPENID_REDIRECT_NEXT variable.
    If none of these urls are set user is redirectd to /.

    if openid isn't registered user is redirected to register page.
    """

    openid=from_openid_response(openid_response)
    request.session['openid']=openid

    try:
        rel = UserAssociation.objects.get(openid_url__exact=str(openid))
    except:
        # try to register this new user
        return register(request)
    u = rel.user
    if u.is_active:
        u.backend = "django.contrib.auth.backends.ModelBackend"
        login(request,u)

    next = request.GET.get('next', '').strip()
    if not next or not is_valid_next_url(next):
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
    
    return HttpResponseRedirect(next)

def is_association_exist(openid_url):
    """ test if an openid is already in database """
    is_exist=True
    try:
        o=UserAssociation.objects.get(openid_url__exact=openid_url)
    except:
        is_exist=False
    return is_exist

def register(request):
    """
    register an openid.

    If user is already a member he can associate its openid with 
    its account.

    A new account could also be created and automaticaly associated
    to the openid.

    url : /complete/

    template : authopenid/complete.html
    """

    is_redirect = False
    next = request.GET.get('next', '').strip()
    if not next or not is_valid_next_url(next):
        next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')


    openid = request.session.get('openid', None)
    if not openid:
         return HttpResponseRedirect(reverse('user_signin') + next)

    nickname = openid.sreg.get('nickname', '')
    email = openid.sreg.get('email', '')
    
    form1 = OpenidRegisterForm(initial={
        'next': next,
        'username': nickname,
        'email': email,
    }) 
    form2 = OpenidVerifyForm(initial={
        'next': next,
        'username': nickname,
    })
    
    if request.POST:
        just_completed=False
        if 'bnewaccount' in request.POST.keys():
            form1 = OpenidRegisterForm(request.POST)
            if form1.is_valid():
                next = form1.cleaned_data['next']
                if not next:
                    next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
                is_redirect = True
                tmp_pwd = User.objects.make_random_password()
                u = User.objects.create_user(form1.cleaned_data['username'],form1.cleaned_data['email'], tmp_pwd)
                
                # make association with openid
                ua = UserAssociation(openid_url=str(openid),user_id=u.id)
                ua.save()
                    
                # login 
                u.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, u)
        elif 'bverify' in request.POST.keys():
            form2 = OpenidVerifyForm(request.POST)
            if form2.is_valid():
                is_redirect = True
                next = form2.cleaned_data['next']
                if not next:
                    next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
                u = form2.get_user()

                ua = UserAssociation(openid_url=str(openid),user_id=u.id)
                ua.save()
                login(request, u)
        
        # redirect, can redirect only if forms are valid.
        if is_redirect:
            return HttpResponseRedirect(next)
    
    
    
    return render('authopenid/complete.html', {
        'form1': form1,
        'form2': form2,
        'action': reverse('user_register'),
        'nickname': nickname,
        'email': email
    }, context_instance=RequestContext(request))

def signin_failure(request, message):
    """
    falure with openid signin. Go back to signin page.

    template : "authopenid/signin.html"
    """
    next = request.REQUEST.get('next', '')

    form_signin = OpenidSigninForm(initial={'next':next})
    form_auth = OpenidAuthForm(initial={'next':next})

    return render('authopenid/signin.html', {
        'msg': message,
        'form1': form_auth,
        'form2': form_signin,
    }, context_instance=RequestContext(request))


def signup(request):
    """
    signup page. Create a legacy account

    url : /signup/"

    templates: authopenid/signup.html, authopenid/confirm_email.txt
    """
    action_signin = reverse('user_signin')

    next = request.GET.get('next', '')
    form = RegistrationForm(initial={'next':next})
    form_signin = OpenidSigninForm(initial={'next':next})

    if request.user.is_authenticated():
        return HttpResponseRedirect(next)
    
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():

            next = form.cleaned_data.get('next', '')

            user = User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['email'], form.cleaned_data['password1'])
           
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            
            # send email
            current_domain = Site.objects.get_current().domain
            subject = _("Welcome")
            message_template = loader.get_template('authopenid/confirm_email.txt')
            message_context = Context({ 'site_url': 'http://%s/' % current_domain,
                                        'username': form.cleaned_data['username'],
                                        'password': form.cleaned_data['password1'] })
            message = message_template.render(message_context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            
            return HttpResponseRedirect(next)
    
    return render('authopenid/signup.html', {
        'form': form,
        'form2': form_signin,
        'action': request.path,
        'action_signin': action_signin,
        },context_instance=RequestContext(request))

@login_required
def signout(request):
    """
    signout from the website. Remove openid from session and kill it.

    url : /signout/"
    """
    try:
        del request.session['openid']
    except KeyError:
        pass
    next = request.GET.get('next', '/')
    if not is_valid_next_url(next):
        next = '/'

    logout(request)
    
    return HttpResponseRedirect(next)


@login_required
@username_control ('user_account_settings')
def account_settings(request,username=None):
    """
    index pages to changes some basic account settings :
     - change password
     - change email
     - associate a new openid
     - delete account

    url : /username/

    template : authopenid/settings.html
    """
    msg = request.GET.get('msg', '')
    is_openid = True

    try:
        o=UserAssociation.objects.get(user__username__exact=username)
    except:
        is_openid = False


    return render('authopenid/settings.html',
            {'msg': msg, 'settings_path': request.path, 'is_openid': is_openid},
            context_instance=RequestContext(request))

@login_required
@username_control('user_changepw')
def changepw(request,username):
    """
    change password view.

    url : /username/changepw/
    template: authopenid/changepw.html
    """
    
    u = get_object_or_404(User, username=username)
    
    if request.POST:
        form = ChangepwForm(request.POST)
        if form.is_valid():
            u.set_password(form.cleaned_data['password1'])
            u.save()
            msg=_("Password changed.") 
            redirect="%s?msg=%s" % (reverse('user_account_settings',kwargs={'username': request.user.username}),urlquote_plus(msg))
            return HttpResponseRedirect(redirect)
    else:
        form=ChangepwForm(initial={'username':request.user.username})

    return render('authopenid/changepw.html', {'form': form },
                                context_instance=RequestContext(request))

@login_required
@username_control('user_changeemail')
def changeemail(request,username):
    """ 
    changeemail view. It require password or openid to allow change.

    url: /username/changeemail/

    template : authopenid/changeemail.html
    """

    extension_args = {}
 
    u = get_object_or_404(User, username=username) 
    
    redirect_to = get_url_host(request) + reverse('user_changeemail',kwargs={'username':username})

    if request.POST:
        form = ChangeemailForm(request.POST)
        if form.is_valid():
            if not form.test_openid:
                u.email = form.cleaned_data['email']
                u.save()
                msg=_("Email changed.") 
                redirect="%s?msg=%s" % (reverse('user_account_settings', kwargs={'username': request.user.username}),urlquote_plus(msg))
                return HttpResponseRedirect(redirect)
            else:
                request.session['new_email'] = form.cleaned_data['email']
                return ask_openid(request, form.cleaned_data['password'], redirect_to, on_failure=emailopenid_failure)    
    elif not request.POST and 'openid.mode' in request.GET:
        return complete(request, emailopenid_success, emailopenid_failure, redirect_to) 
    else:
        form = ChangeemailForm(initial={
                                        'email': u.email,
                                        'username':request.user.username
                                        })
    
    return render('authopenid/changeemail.html', 
            {'form': form }, context_instance=RequestContext(request))

def emailopenid_success(request, identity_url, openid_response):
    openid=from_openid_response(openid_response)

    try:
        u=User.objects.get(username=request.user.username)
    except:
        raise Http404

    try:
        o=UserAssociation.objects.get(openid_url__exact=identity_url)
    except:
        return emailopenid_failure(request, _("No openid % associated in our database" % identity_url))

    if o.user.username != request.user.username:
        return emailopenid_failure(request, _("The openid %s isn't associated to current logged user" % identity_url))
    
    new_email=request.session.get('new_email', '')
    if new_email:
        u.email=new_email
        u.save()
        del request.session['new_email']
    msg=_("Email Changed.")

    redirect="%s?msg=%s" % (reverse('user_account_settings',kwargs={'username': request.user.username}),urlquote_plus(msg))
    return HttpResponseRedirect(redirect)
    

def emailopenid_failure(request, message):
    redirect_to="%s?msg=%s" % (reverse('user_changeemail',kwargs={'username':request.user.username}), urlquote_plus(message))

    return HttpResponseRedirect(redirect_to)
 

@login_required
@username_control('user_changeopenid')
def changeopenid(request, username):
    """
    change openid view. Allow user to change openid associated to its username.

    url : /username/changeopenid/

    template: authopenid/changeopenid.html
    """

    extension_args = {}
    openid_url=''
    has_openid=True
    msg = request.GET.get('msg', '')
        
    u = get_object_or_404(User, username=username)

    try:
        uopenid=UserAssociation.objects.get(user=u)
        openid_url = uopenid.openid_url
    except:
        has_openid=False
    
    redirect_to = get_url_host(request) + reverse('user_changeopenid',kwargs={'username':username})
    if request.POST and has_openid:
        form=ChangeopenidForm(request.POST)
        if form.is_valid():
            return ask_openid(request, form.cleaned_data['openid_url'], redirect_to, on_failure=changeopenid_failure)
    elif not request.POST and has_openid:
        if 'openid.mode' in request.GET:
            return complete(request, changeopenid_success, changeopenid_failure, redirect_to)    

    form = ChangeopenidForm(initial={'openid_url': openid_url, 'username':request.user.username })
    return render('authopenid/changeopenid.html', {'form': form,
        'has_openid': has_openid, 'msg': msg }, context_instance=RequestContext(request))


def changeopenid_success(request, identity_url, openid_response):
    openid=from_openid_response(openid_response)
    is_exist=True
    try:
        o=UserAssociation.objects.get(openid_url__exact=identity_url)
    except:
        is_exist=False
        
    if not is_exist:
        try:
            o=UserAssociation.objects.get(user__username__exact=request.user.username)
            o.openid_url=identity_url
            o.save()
        except:
            o=UserAssociation(user=request.user,openid_url=identity_url)
            o.save()
    elif o.user.username != request.user.username:
        return changeopenid_failure(request, _('This openid is already associated with another account.'))

    request.session['openids'] = []
    request.session['openids'].append(openid)

    msg=_("Openid %s associated with your account." % identity_url) 
    redirect="%s?msg=%s" % (reverse('user_account_settings', kwargs={'username':request.user.username}), urlquote_plus(msg))
    return HttpResponseRedirect(redirect)
    

def changeopenid_failure(request, message):
    redirect_to="%s?msg=%s" % (reverse('user_changeopenid',kwargs={'username':request.user.username}), urlquote_plus(message))
    return HttpResponseRedirect(redirect_to)
  

@login_required
@username_control('user_delete')
def delete(request,username):
    """
    delete view. Allow user to delete its account. Password/openid are required to 
    confirm it. He should also check the confirm checkbox.

    url : /username/delete

    template : authopenid/delete.html
    """

    extension_args={}
    
    u = get_object_or_404(User, username=username)

    redirect_to = get_url_host(request) + reverse('user_delete',kwargs={'username':username}) 
    if request.POST:
        form = DeleteForm(request.POST)
        if form.is_valid():
            if not form.test_openid:
                u.delete() 
                return signout(request)
            else:
                return ask_openid(request, form.cleaned_data['password'], redirect_to, on_failure=deleteopenid_failure)
    elif not request.POST and 'openid.mode' in request.GET:
        return complete(request, deleteopenid_success, deleteopenid_failure, redirect_to) 
    
    form = DeleteForm(initial={'username': username})

    msg = request.GET.get('msg','')
    return render('authopenid/delete.html', {'form': form, 'msg': msg, },
                                        context_instance=RequestContext(request))


def deleteopenid_success(request, identity_url, openid_response):
    openid=from_openid_response(openid_response)

    try:
        u=User.objects.get(username=request.user.username)
    except:
        raise Http404

    try:
        o=UserAssociation.objects.get(openid_url__exact=identity_url)
    except:
        return deleteopenid_failure(request, _("No openid % associated in our database" % identity_url))

    if o.user.username == request.user.username:
        u.delete()
        return signout(request)
    else:
        return deleteopenid_failure(request, _("The openid %s isn't associated to current logged user" % identity_url))
    
    msg=_("Account deleted.") 
    redirect="/?msg=%s" % (urlquote_plus(msg))
    return HttpResponseRedirect(redirect)
    

def deleteopenid_failure(request, message):
    redirect_to="%s?msg=%s" % (reverse('user_delete',kwargs={'username':request.user.username}), urlquote_plus(message))

    return HttpResponseRedirect(redirect_to)


def sendpw(request):
    """
    send a new password to the user. It return a mail with 
    a new pasword and a confirm link in. To activate the 
    new password, the user should click on confirm link.

    url : /sendpw/

    templates :  authopenid/sendpw_email.txt, authopenid/sendpw.html
    """

    msg = request.GET.get('msg','')
    if request.POST:
        form = EmailPasswordForm(request.POST)
        if form.is_valid():
            new_pw = User.objects.make_random_password()
            confirm_key = UserPasswordQueue.objects.get_new_confirm_key()
            try:
                q=UserPasswordQueue.objects.get(user=form.user_cache)
            except:
                q=UserPasswordQueue(user=form.user_cache)
            q.new_password=new_pw
            q.confirm_key = confirm_key
            q.save()
            # send email
            from django.core.mail import send_mail
            current_domain = Site.objects.get_current().domain
            subject = _("Request for a new password")
            message_template = loader.get_template('authopenid/sendpw_email.txt')
            message_context = Context({ 'site_url': 'http://%s' % current_domain,
                'confirm_key': confirm_key,
                'username': form.user_cache.username,
                'password': new_pw,
                'url_confirm': reverse('user_confirmchangepw'),
            })
            message = message_template.render(message_context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [form.user_cache.email])
            msg=_("A new password has been sent to your email")
    else:
        form = EmailPasswordForm()
        
    return render('authopenid/sendpw.html', {'form': form,
            'msg': msg, },
            context_instance=RequestContext(request))


def confirmchangepw(request):
    """
    view to set new password when the user click on confirm link
    in its mail. Basically it check if the confirm key exist, then
    replace old password with new password and remove confirm
    ley from the queue. Then it redirect the user to signin
    page.

    url : /sendpw/confirm/?key

    """


    confirm_key = request.GET.get('key', '')
    if not confirm_key:
        return HttpResponseRedirect('/')

    try:
        q = UserPasswordQueue.objects.get(confirm_key__exact=confirm_key)
    except:
        msg=_("Can not change password. Confirmation key '%s' isn't registered." % confirm_key) 
        redirect="%s?msg=%s" % (reverse('user_sendpw'),urlquote_plus(msg))
        return HttpResponseRedirect(redirect)

    try:
        user = User.objects.get(id=q.user.id)
    except:
        msg=_("Can not change password. User don't exist anymore in our database.") 
        redirect="%s?msg=%s" % (reverse('user_sendpw'),urlquote_plus(msg))
        return HttpResponseRedirect(redirect)

    user.set_password(q.new_password)
    user.save()
    q.delete()
    msg=_("Password changed for %s. You could now sign-in" % user.username) 
    redirect="%s?msg=%s" % (reverse('user_signin'), 
                                        urlquote_plus(msg))

    return HttpResponseRedirect(redirect)
