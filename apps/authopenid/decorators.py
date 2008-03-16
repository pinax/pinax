# -*- coding: utf-8 -*-
"""
 Copyright (c) 2007, Benoît Chesneau

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
from django.http import HttpResponseRedirect
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import reverse



def username_control(view_name):
    """
    decorator that test if user is authenticated and if
    username in request.path is the one used by authenticated
    user.

    if user isn't authenticated it redirect him to signin page.
    If username != username authenticated, it redirect to
    the "good" page. Url is also changed.
    """

    def _username_controller(view_func):
        def _username_controlled(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            username = None
            if 'username' in kwargs:
                username = kwargs['username']

            if not username or username!=request.user.username: 
                kwargs['username'] = request.user.username
                redirect_to=iri_to_uri(reverse(view_name, kwargs=kwargs))
                return HttpResponseRedirect(redirect_to)

            return response
        return _username_controlled

    return _username_controller


