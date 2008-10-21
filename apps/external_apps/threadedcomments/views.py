from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, Template
from django.utils.http import urlquote
from django.conf import settings
from forms import FreeThreadedCommentForm, ThreadedCommentForm
from models import ThreadedComment, FreeThreadedComment, DEFAULT_MAX_COMMENT_LENGTH
from utils import JSONResponse, XMLResponse

def _adjust_max_comment_length(form, field_name='comment'):
    """
    Sets the maximum comment length to that default specified in the settings.
    """
    form.base_fields['comment'].max_length = DEFAULT_MAX_COMMENT_LENGTH

def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they 
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    4. Otherwise, the view raise a 404 Not Found.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next or next == request.path:
        raise Http404 # No next url was supplied in GET or POST.
    return next

def _preview(request, context_processors, extra_context, form_class=ThreadedCommentForm):
    """
    Returns a preview of the comment so that the user may decide if he or she wants to
    edit it before submitting it permanently.
    """
    _adjust_max_comment_length(form_class)
    form = form_class(request.POST or None)
    context = {
        'next' : _get_next(request),
        'form' : form,
    }
    if form.is_valid():
        new_comment = form.save(commit=False)
        context['comment'] = new_comment
    else:
        context['comment'] = None
    return render_to_response(
        'threadedcomments/preview_comment.html',
        extra_context, 
        context_instance = RequestContext(request, context, context_processors)
    )

def free_comment(request, content_type=None, object_id=None, edit_id=None, parent_id=None, add_messages=False, ajax=False, model=FreeThreadedComment, form_class=FreeThreadedCommentForm, context_processors=[], extra_context={}):
    """
    Receives POST data and either creates a new ``ThreadedComment`` or 
    ``FreeThreadedComment``, or edits an old one based upon the specified parameters.

    If there is a 'preview' key in the POST request, a preview will be forced and the
    comment will not be saved until a 'preview' key is no longer in the POST request.
    
    If it is an *AJAX* request (either XML or JSON), it will return a serialized
    version of the last created ``ThreadedComment`` and there will be no redirect.
    
    If invalid POST data is submitted, this will go to the comment preview page
    where the comment may be edited until it does not contain errors.
    """
    if not edit_id and not (content_type and object_id):
        raise Http404 # Must specify either content_type and object_id or edit_id
    if "preview" in request.POST:
        return _preview(request, context_processors, extra_context, form_class=form_class)
    if edit_id:
        instance = get_object_or_404(model, id=edit_id)
    else:
        instance = None
    _adjust_max_comment_length(form_class)
    form = form_class(request.POST, instance=instance)
    if form.is_valid():
        new_comment = form.save(commit=False)
        if not edit_id:
            new_comment.ip_address = request.META.get('REMOTE_ADDR', None)
            new_comment.content_type = get_object_or_404(ContentType, id = int(content_type))
            new_comment.object_id = int(object_id)
        if model == ThreadedComment:
            new_comment.user = request.user
        if parent_id:
            new_comment.parent = get_object_or_404(model, id = int(parent_id))
        new_comment.save()
        if model == ThreadedComment:
            if add_messages:
                request.user.message_set.create(message="Your message has been posted successfully.")
        else:
            request.session['successful_data'] = {
                'name' : form.cleaned_data['name'],
                'website' : form.cleaned_data['website'],
                'email' : form.cleaned_data['email'],
            }
        if ajax == 'json':
            return JSONResponse([new_comment,])
        elif ajax == 'xml':
            return XMLResponse([new_comment,])
        else:
            return HttpResponseRedirect(_get_next(request))
    elif ajax=="json":
        return JSONResponse({'errors' : form.errors}, is_iterable=False)
    elif ajax=="xml":
        template_str = """
<errorlist>
    {% for error,name in errors %}
    <field name="{{ name }}">
        {% for suberror in error %}<error>{{ suberror }}</error>{% endfor %}
    </field>
    {% endfor %}
</errorlist>
        """
        response_str = Template(template_str).render(Context({'errors' : zip(form.errors.values(), form.errors.keys())}))
        return XMLResponse(response_str, is_iterable=False)
    else:
        return _preview(request, context_processors, extra_context, form_class=form_class)
      
def comment(*args, **kwargs):
    """
    Thin wrapper around free_comment which adds login_required status and also assigns
    the ``model`` to be ``ThreadedComment``.
    """
    kwargs['model'] = ThreadedComment
    kwargs['form_class'] = ThreadedCommentForm
    return free_comment(*args, **kwargs)
# Require login to be required, as request.user must exist and be valid.
comment = login_required(comment)

def can_delete_comment(comment, user):
    """
    Default callback function to determine wether the given user has the
    ability to delete the given comment.
    """
    if user.is_staff or user.is_superuser:
        return True
    if hasattr(comment, 'user') and comment.user == user:
        return True
    return False

def comment_delete(request, object_id, model=ThreadedComment, extra_context = {}, context_processors = [], permission_callback=can_delete_comment):
    """
    Deletes the specified comment, which can be either a ``FreeThreadedComment`` or a
    ``ThreadedComment``.  If it is a POST request, then the comment will be deleted
    outright, however, if it is a GET request, a confirmation page will be shown.
    """
    tc = get_object_or_404(model, id=int(object_id))
    if not permission_callback(tc, request.user):
        login_url = settings.LOGIN_URL
        current_url = urlquote(request.get_full_path())
        return HttpResponseRedirect("%s?next=%s" % (login_url, current_url))
    if request.method == "POST":
        tc.delete()
        return HttpResponseRedirect(_get_next(request))
    else:
        if model == ThreadedComment:
            is_free_threaded_comment = False
            is_threaded_comment = True
        else:
            is_free_threaded_comment = True
            is_threaded_comment = False
        return render_to_response(
            'threadedcomments/confirm_delete.html',
            extra_context, 
            context_instance = RequestContext(
                request, 
                {
                    'comment' : tc, 
                    'is_free_threaded_comment' : is_free_threaded_comment,
                    'is_threaded_comment' : is_threaded_comment,
                    'next' : _get_next(request),
                },
                context_processors
            )
        )