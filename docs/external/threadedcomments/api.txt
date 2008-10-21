==================================
threadedcomments API Documentation
==================================

.. contents:: Table of Contents
    :backlinks: none

Models
======

*threadedcomments* has two basic models that are included and supported by
default: ``ThreadedComment``, and ``FreeThreadedComment``.  The difference
between these two models is slight.  In essence, every ``ThreadedComment`` 
instance is associated with a user from ``django.contrib.auth.models.User``.
While ``FreeThreadedComment`` has no such user association, it provides a few
other identifying fields instead.

Common Fields
-------------

Below is a listing of all of the fields that are shared by both 
``ThreadedComment`` and ``FreeThreadedComment``.

These first three fields deal with the object with which this comment is
associated:

:``content_type`` [``ForeignKey``]:
    **required** The content type 
    (``django.contrib.contenttypes.models.ContentType``) instance with which 
    this comment is associated.

:``object_id`` [``PositiveIntegerField``]:
    **required** The value of the primary key to which this comment is 
    associated.

:``content_object`` [``GenericForeignKey``]:
    Combines the ``content_type`` and ``object_id`` fields to act as a
    virtual foreign key to the associated object.

The next field is how we build our "threads", or hierarchy:

:``parent`` [``ForeignKey``]:
    A self-referencing foreign key to whom this comment is addressed, 
    being ``None`` if it is a toplevel comment (addressed directly to 
    the original content object).

The following fields deal with keeping track of dates of some events on 
this comment:

:``date_submitted`` [``DateTimeField``]:
    The date and time that this comment was saved for the first time.

:``date_modified`` [``DateTimeField``]:
    The most recent date and time that this comment was saved.

:``date_approved`` [``DateTimeField``]:
    The date and time that this comment set as ``is_approved=True``.

The following fields deal with the actual content of the comment itself:

:``comment`` [``TextField``]:
    **required** The content of the comment.

:``markup`` [``IntegerField``]:
    **required** The format of the comment.  Values may be ``MARKDOWN``, 
    ``TEXTILE``, ``REST``, ``PLAINTEXT``.  This can be used for display
    purposes when deciding how to format the comment for viewing.

The following fields have to do with the status of the comment.  Combined,
they describe whether the comment should be viewable or not:

:``is_public`` [``BooleanField``]:
    **required** This field defaults to ``True``, but will bet set to 
    ``False`` if any of the moderation checks in an associated ``Moderator`` 
    fail.

:``is_approved`` [``BooleanField``]:
    **required** This field defaults to ``False``, and it acts as an 
    administrative override.  It allows administrators to manually "whitelist"
    comments which fail a moderation test resulting in ``is_public``
    being set to ``False``.

The following field is extra metadata that may be generally useful:

:``ip_address`` [``IPAddressField``]:
    This field stores the IP address of the computer that is submits the
    comment.

``ThreadedComment``
-------------------

``ThreadedComment`` is useful for allowing registered users to comment. It is
for this reason that there is a required foreign key to ``User``.

:``user`` [``ForeignKey``]:
    Associates this comment with a particular user from 
    ``django.contrib.auth.models.User``.


``FreeThreadedComment``
-----------------------

``FreeThreadedComment`` is better suited for allowing just about anyone to
post comments on an item.  Instead of being associated with a particular user,
instead it asks for some additional information like name and e-mail.

:``name`` [``CharField``]:
    **required** The name of the person leaving the comment.

:``website`` [``URLField``]:
    If the person leaving the comment runs or is affiliated with a website,
    this is where that information would be stored.

:``email`` [``EmailField``]:
    An e-mail address where the person leaving the comment can be reached.

Custom Managers
===============

Since it's not a feature of most databases to store hierarchical information,
some methods are needed to be able to access that hierarchical information in a
meaningful way.  Also, since these comment objects can attach to any object,
some convenience methods are helpful to query for and to create comments.  
These types of methods do not belong on the model itself, but rather on the 
``Manager``.

Common Methods
--------------

:``get_tree(content_object, root=None)``:
    Runs a depth-first search on all of the comments attached to the given
    content object.  It then annotates a ``depth`` field which is an integer 
    representing how many nodes away it is from the root node (the content
    object itself).  It also orders the comments appropriately into threads.  If
    a root comment is specified, the comment tree will start at that specific
    comment.  This way, one could get a single thread of the comments.

:``create_for_object(content_object, **kwargs)``:
    Wraps the ``create`` method, and automatically fills out ``content_type``
    and ``object_id`` fields based on those given by the content object.

:``get_or_create_for_object(content_object, **kwargs)``:
    Wraps the ``get_or_create`` method, and automatically fills out 
    ``content_type`` and ``object_id`` fields based on those given by the 
    content object.

:``get_for_object(content_object, **kwargs)``:
    Wraps the ``get`` method, and automatically fills out ``content_type``
    and ``object_id`` fields based on those given by the content object.

:``all_for_object(content_object, **kwargs)``:
    Prepopulates a QuerySet with all comments related to the given 
    ``content_object``.


``ThreadedCommentManager``
--------------------------

This manager simply adds all of the aformentioned common methods onto the 
default manager.

It can be used by using the ``objects`` property on either ``ThreadedComment`` 
or ``FreeThreadedComment``.  An example would be::

    >>> FreeThreadedComment.objects.all()
    [<FreeThreadedComment: This is a test.>, <FreeThreadedComment: spam>]

``PublicThreadedCommentManager``
--------------------------------

This manager adds all of the aformentioned common methods onto the default
manager, and then restricts all results to either be ``is_public = True`` or
(by way of administrative override) ``is_approved = True``.

It can be used by using the ``public`` property on either ``ThreadedComment`` 
or ``FreeThreadedComment``.  An example would be::

    >>> FreeThreadedComment.public.all()
    [<FreeThreadedComment: This is a test.>]

Moderation
==========

Moderation is how you are able to assign custom functionality to comments.  
Almost all moderation settings take place by registering moderator objects in 
lieu of Django settings.  This means that you may choose different options for
comments on different pages, etc.

*threadedcomments* uses a customized version of _django-comment-utils for its 
comment moderation.  If you have used _django-comment-utils with the built-in
``django.contrib.comments`` application, you will find all of this very 
familiar.

.. caution::

    Prior to version 0.3, *threadedcomments* used a custom moderation system,
    however, due to a lack of robustness in the included implementation,
    django-comment-utils is now a required dependency.
    This is a backwards-incompatible change, so take care when upgrading to
    re-visit your old moderation code.

.. _django-comment-utils: http://code.google.com/p/django-comment-utils/

In ``threadedcomments.moderation`` there exists two items of note:

1. ``CommentModerator``, which subclasses ``comment_utils.CommentModerator``.
   You can subclass this to provide moderation functionality for your content 
   objects.

2. ``moderator``, an instance of ``Moderator``, which subclasses 
   ``comment_utils.Moderator``.  It is with this that you will register your
   ``CommentModerator`` objects.

Additional ``CommentModerator`` Properties
------------------------------------------

``CommentModerator`` has many different properties, most of which are listed in
the `django-comment-utils documentation`_.  Listed below are the extra 
properties that can be set by using the ``CommentModerator`` provided by
*threadedcomments*.

.. _`django-comment-utils documentation`: http://django-comment-utils.googlecode.com/svn/trunk/docs/

:``max_comment_length``:
    The maximum length of a comment, in characters.  Defaults to 
    ``settings.DEFAULT_MAX_COMMENT_LENGTH``.  If a comment goes beyond this 
    length, the manager will set ``is_public = False`` before saving.

:``allowed_markup``:
    A list of which markup types this manager will allow.  If a different
    markup is submitted, the manager will set ``is_public = False`` before
    saving.

    This list can be comprised of zero or more of the following imported 
    constants::
        
        from threadedcomments.models import MARKDOWN, TEXTILE, REST, PLAINTEXT

:max_depth:
    The maximum "depth" of a comment.  That is, it will take no more than 
    max_depth parent relationship traversals to hit a comment with no parent.
    Defaults to ``settings.DEFAULT_MAX_COMMENT_DEPTH``.  If a comment goes 
    beyond this depth, the manager will set ``is_public = False`` before 
    saving.

Model-Manager Registration
--------------------------

To register a manager with a model, first the moderator must be imported::

    from threadedcomments.moderation import moderator

Then, the moderator has ``register`` and ``unregister`` functions.

:``register(model, moderator)``:
    Registers a model class with a manager or with the aformentioned keyword
    arguments.

:``unregister(model)``:
    Unregisters the manager that's currently associated with the given model.

Example
-------

The following example will assume that a "BlogPost" model exists::

    class BlogPost(models.Model):
        title = models.CharField(max_length=128)
        body = models.TextField()
        allows_comments = models.BooleanField(default = True)

Using ``CommentModerator``::

    from threadedcomments.moderation import moderator, CommentModerator

    class BlogPostModerator(CommentModerator):
        akismet = True
        enable_field = 'allows_comments'
        max_depth = 5

    moderator.register(BlogPost, BlogPostModerator)

What this has done is ensure that if allows_comments is set to false, all
comments will be deleted.  Also, the maximum depth of the comment tree will
be 5 comments deep.  Finally, each comment will be spam-checked by Akismet_.

.. _Akismet: http://akismet.com/

Template Helpers
================

While it's possible to import the comment models and use them to query for the
appropriate comments, sometimes it's easier to do some of that manipulation
in the template.  There are several tags and filters which will help to begin
using *threadedcomments*.

To use any of these tags or filters, first make sure to have 'threadedcomments'
listed in your ``INSTALLED_APPS``, and then include the following in your
template::

    {% load threadedcommentstags %}

After "threadedcommentstags" has been loaded, all of the following become
available.

Tags
----

:``{% get_comment_url OBJECT [PARENT=None] %}``:
    Gets the URL to post to for the given object and optional parent comment.

:``{% get_comment_url_json OBJECT [PARENT=None] %}``:
    Gets the URL to post to for the given object and optional parent comment, 
    which will respond with JSON (useful for AJAX).

:``{% get_comment_url_xml OBJECT [PARENT=None] %}``:
    Gets the URL to post to for the given object and optional parent comment, 
    which will respond with XML (useful for AJAX).

:``{% get_free_comment_url OBJECT [PARENT=None] %}``:
    Gets the URL to post to for the given object and optional parent free 
    comment.

:``{% get_free_comment_url_json OBJECT [PARENT=None] %}``:
    Gets the URL to post to for the given object and optional parent free 
    comment, which will respond with JSON (useful for AJAX).

:``{% get_free_comment_url_xml OBJECT [PARENT=None] %}``:
    Gets the URL to post to for the given object and optional parent free 
    comment, which will respond with XML (useful for AJAX).

:``{% get_comment_count for OBJECT as CONTEXT_VAR %}``:
    Calls ``ThreadedComment.public.all_for_object(OBJECT).count()`` and places 
    the result into the specified context variable.

:``{% get_free_comment_count for OBJECT as CONTEXT_VAR %}``:
    Calls ``FreeThreadedComment.public.all_for_object(OBJECT).count()`` and 
    places the result into the specified context variable.

:``{% auto_transform_markup COMMENT [as CONTEXT_VAR] %}``:
    Inspects the given comment and its markup, and either outputs it using the
    correct markup processor, or if a context variable is specified, outputs
    it into the context for further use.

:``{% get_threaded_comment_tree for OBJECT [TREE_ROOT] as CONTEXT_VAR %}``:
    Calls ``ThreadedComment.public.get_tree(OBJECT)`` and places the result 
    into the specified context variable.  TREE_ROOT is an optional comment
    or comment_id, which would be the root of the tree.  This way, querying for
    a single thread of comments is made easy.

:``{% get_free_threaded_comment_tree for OBJECT [TREE_ROOT] as CONTEXT_VAR %}``:
    Calls ``FreeThreadedComment.public.get_tree(OBJECT)`` and places the result 
    into the specified context variable.  TREE_ROOT is an optional comment
    or comment_id, which would be the root of the tree.  This way, querying for
    a single thread of comments is made easy.

:``{% get_threaded_comment_form as CONTEXT_VAR %}``:
    Gets an unbound ``ThreadedCommentForm`` and assigns it to the specified
    context variable.

:``{% get_free_threaded_comment_form as CONTEXT_VAR %}``:
    Gets an unbound ``FreeThreadedCommentForm`` and assigns it to the specified
    context variable.

:``{% get_latest_comments NUM_TO_GET as CONTEXT_VAR %}``:
    Gets the ``NUM_TO_GET`` latest ``ThreadedComment`` instances, ordered by
    ``date_submitted`` and assigns it to the specified context variable.

:``{% get_latest_free_comments NUM_TO_GET as CONTEXT_VAR %}``:
    Gets the ``NUM_TO_GET`` latest ``FreeThreadedComment`` instances, ordered 
    by ``date_submitted`` and assigns it to the specified context variable.

:``{% get_user_comments for USERNAME as CONTEXT_VAR %}``:
    Gets the comments submitted by ``USERNAME``, and assigns it to the specified
    context variable.

:``{% get_user_comment_count for USERNAME as CONTEXT_VAR %}``:
    Gets the number of comments submitted by ``USERNAME``, and assigns it to the
    specified context variable.

Filters
-------

:oneline:
    Gets rid of all newlines and spaces in-between tags.  This is useful for
    calling when passing, for example, a form to javascript.  You could use it
    like so::

        <script type="text/javascript">
            var form_html_fragment = '{{ form.as_ul|oneline }}';
        </script>

    Now you could use that ``form_html_fragment`` Javascript variable to 
    dynamically add or remove comment forms to the page.

Gravatar Support
----------------

*threadedcomments* now has support built-in for Gravatar_, the "globally 
recognized avatar" system provided by Automattic_.  To use this functionality,
load the gravatar template tags in your template like so::

    {% load gravatar %}

.. _Gravatar: http://site.gravatar.com/
.. _Automattic: http://automattic.com/

After the gravatar template library has been loaded, a new tag and filter 
become available.

Gravatar Tag
~~~~~~~~~~~~

Generates a gravatar image URL based on the given parameters.
    
Format is as follows (The square brackets indicate that those arguments are 
optional.)::

    {% get_gravatar_url for emailvar [rating "R" size 80 default img:blank as contextvar] %}

Rating, size, and default may be either literal values or template variables.
The template tag will attempt to resolve variables first, and on resolution
failure it will use the literal value.

If ``as`` is not specified, the URL will be output to the template in place.

For all other arguments that are not specified, the appropriate default 
settings attribute will be used instead. See the **Gravatar** portion of the 
Settings_ section to see what those defaults are.

Gravatar Filter
~~~~~~~~~~~~~~~

Generates a gravatar image URL based on the email address string provided and 
settings or defaults.

The best way to describe this filter is to show an example::

    <img src="{{ user.email|gravatar }}" alt="Gravatar for {{ user.get_full_name }}" />

In this example, we have a standard Django user object.  We're using the e-mail
address for that user to generate a gravatar image and the other attributes
from that user to generate some alternate text for accessibility.

The maximum rating, default image, and image size of this gravatar are a result
of the gravatar-specific settings provided.  See the **Gravatar** portion of
the Settings_ section to see what those settings are.

Views
=====

There are three basic view types included with threadedcomments: **create**, 
**edit**, and **delete**.  The following are the URL names and what inputs they 
take.

**Create**
----------

:``tc_comment``:

    :``content_type``:
        The content type of the model to attach to.

    :``object_id``:
        The primary key of the model to attach to.

:``tc_comment_parent``:

    :``content_type``:
        The content type of the model to attach to.

    :``object_id``:
        The primary key of the model to attach to.

    :``parent_id``:
        The primary key of the parent comment to which this comment is a
        response.

:``tc_comment_ajax``:

    :``content_type``:
        The content type of the model to attach to.

    :``object_id``:
        The primary key of the model to attach to.

    :``ajax``:
        'json' or 'xml', depending on the response type that is wanted.

:``tc_comment_parent_ajax``:

    :``content_type``:
        The content type of the model to attach to.

    :``object_id``:
        The primary key of the model to attach to.

    :``parent_id``:
        The primary key of the parent comment to which this comment is a
        response.

    :``ajax``:
        'json' or 'xml', depending on the response type that is wanted.

:``tc_free_comment``:
    The same as ``tc_comment``, only it deals with ``FreeThreadedComment`` 
    model objects instead of ``ThreadedComment`` objects.

:``tc_free_comment_parent``:
    The same as ``tc_comment_parent``, only it deals with 
    ``FreeThreadedComment`` model objects instead of ``ThreadedComment`` 
    objects.

:``tc_free_comment_ajax``:
    The same as ``tc_comment_ajax``, only it deals with ``FreeThreadedComment`` 
    model objects instead of ``ThreadedComment`` objects.

:``tc_free_comment_parent_ajax``:
    The same as ``tc_comment_parent_ajax``, only it deals with 
    ``FreeThreadedComment`` model objects instead of ``ThreadedComment`` 
    objects.

**Edit**
--------

:``tc_comment_edit``:
    
    :``edit_id``:
        The primary key of the comment that should be edited.

:``tc_comment_edit_ajax``:

    :``edit_id``:
        The primary key of the comment that should be edited.

    :``ajax``:
        'json' or 'xml', depending on the response type that is wanted.

:``tc_free_comment_edit``:
    The same as ``tc_comment_edit``, only it deals with ``FreeThreadedComment``
    model objects instead of ``ThreadedComment`` objects.

:``tc_free_comment_edit_ajax``:
    The same as ``tc_comment_edit_ajax``, only it deals with 
    ``FreeThreadedComment`` model objects instead of ``ThreadedComment`` 
    objects.

**Delete**
----------

:``tc_comment_delete``:

    :``object_id``:
        The primary key of the ``ThreadedComment`` to delete.

:``tc_free_comment_delete``:

    :``object_id``:
        The primary key of the ``FreeThreadedComment`` to delete.

Previewing
----------

If the key 'preview' is inserted into any of the following views, a preview
page ('threadedcomments/preview_comment.html') will be shown:

* ``tc_comment``

* ``tc_comment_parent``

* ``tc_comment_edit``

* ``tc_free_comment``

* ``tc_free_comment_parent``

* ``tc_free_comment_edit``

The context will be:

:next:
    The page to which the user should be redirected after successfully posting
    a comment.  This is usually to be used in a hidden input field in a form
    that tells the view where to go next.

:form:
    Either a ``FreeThreadedCommentForm`` or a ``ThreadedCommentForm``, 
    depending on the type of view.

:comment:
    If the parameters in POST validate correctly with the appropriate form, the
    unsaved comment will be passed in through this variable.

If a GET request is sent to the **Delete** views, a confirmation/preview page
('threadedcomments/confirm_delete.html') will be shown with context:

:comment:
    The comment object to be deleted.

:is_free_threaded_comment:
    True if comment to be deleted is a ``FreeThreadedComment``, and False
    otherwise.

:is_threaded_comment:
    True if comment to be deleted is a ``ThreadedComment``, and False 
    otherwise.

:next:
    The page to which the user should be redirected after successfully deleting
    a comment.  This is usually to be used in a hidden input field in a form
    that tells the view where to go next.

Redirection
-----------

After a comment is posted, choosing where to go next happens in this order:

1. If there exists a ``next`` variable in the POST data, it will redirect 
   there.

2. If there exists a ``next`` variable in the GET data, it will redirect there.

3. If ``HTTP_REFERER`` exists in the request's META information, it will 
   redirect there--as long as it doesn't create an infinite loop.

4. It will raise an ``Http404``.

AJAX
----

*threadedcomments* provides a very basic AJAX implementation.  Upon POSTing to
the view, it will return a JSON or an XML (as requested by URL) representation 
of the object just committed.  It's up to you to dynamically
insert its content into the comment thread.

Errors
------

If a view encounters an error (form validation being the most common case), 
then depending on whether the comment is being created using the JSON, XML, or
plain HTML APIs, different things will occur.  If it's using the JSON API, then
it will return a JSON-formatted error string.  If it's using XML, it will 
return an XML-formatted error string.  Otherwise, it will redirect the user to
a preview page where he/she can edit the comment until it no longer has any
errors.  At this point, the user will be redirected to the page to which they
would have originally been redirected.

.. tip::

    When using ``FreeThreadedComment`` and after a comment is successfully
    saved, the successful ``name``, ``website``, and ``email`` fields will be
    placed into the session under the name ``successful_data``.  To use this
    data for the next time a user visits the website, simply populate the
    initial data for a form with the ``successful_data`` dict.

    For example::

        successful_data = request.session.get('successful_data', {})
        form = FreeThreadedCommentForm(initial = successful_data)

    Now that form will have the user's simple data prepopulated.  It's that
    easy!

Forms
=====

*threadedcomments* provides two basic forms that you can use and/or subclass
to suit your needs: ``ThreadedCommentForm``, and ``FreeThreadedCommentForm``.

``ThreadedCommentForm``
-----------------------

Simply includes two fields: comment, and markup.

:comment:
    **required** The content of the comment.

:markup:
    **required** The type of markup that the comment is using.  This may be 
    easily overridden in a subclass to become a ``HiddenInput``, if the user is 
    not to be given a choice of markup options.

``FreeThreadedCommentForm``
---------------------------

Includes a few fields: comment, name, website, email, and markup.

:comment:
    **required** The content of the comment.

:name:
    **required** The name of the person 

:website:
    A website for the commenter, if he or she has one to list.

:email:
    An e-mail address where the person leaving the comment can be reached.

:markup:
    **required** The type of markup that the comment is using.  This may be 
    esaily overridden in a subclass to become a ``HiddenInput``, if the user is 
    not to be given a choice of markup options.

Settings
========

Most of the configuration will be done via the use of the Moderation_ features
of *threadedcomments* itself, but there are a few settings that you might want 
or need to apply globally in the settings file.

General
-------

:``AKISMET_API_KEY``:
    Your API key for Akismet.  This will only be needed if you enable Akismet
    moderation of comments on one or more of your models.

:``DEFAULT_MAX_COMMENT_LENGTH = 1000``:
    The default max_length that the comment forms should validate against
    if an override isn't specified in per-model moderation.  If this isn't
    specified, then a default DEFAULT_MAX_COMMENT_LENGTH of 1000 is used.

:``DEFAULT_MAX_COMMENT_DEPTH = 8``:
    The default max_depth that the moderation should validate against if it
    isn't explicitly defined in the moderator.  Keep in mind that if no 
    moderator is registered against a model, this default depth will not be
    adhered to either.

:``DEFAULT_MARKUP = PLAINTEXT``:
    Every comment which is added to any object has not only some text, but that
    text may be stored in some markup language like restructured text or
    textile.  If this information is not provided to the form, then the comment 
    will fall back to a default of whatever is specified here.  The default is 
    ``PLAINTEXT``.

Gravatar
--------

:``GRAVATAR_MAX_RATING = "R"``:
    The default maximum rating to display for gravatars.  Can be "G", "PG",
    "R", or "X".

:``GRAVATAR_DEFAULT_IMG = "img:blank"``:
    The full URL to the default image if a gravatar image is not found.

:``GRAVATAR_SIZE = 80``:
    The size in which the gravatar should be displayed.  Values may be from 1
    to 80, inclusive.

More
====

This is as good as it gets for now.  Until more documentation is posted, check 
out `Tutorial 1`_.  Beyond that, there's fairly extensive in-line 
documentation, so you can `browse the source code`_.  If you're the kind of
person who likes to scan doctests, you can check the tests out here_.

.. _`Tutorial 1`: http://api.rst2a.com/1.0/rst2/html?uri=http%3A//django-threadedcomments.googlecode.com/svn/trunk/docs/tutorial.txt&style=zope
.. _`browse the source code`: http://django-threadedcomments.googlecode.com/svn/trunk/
.. _here: http://django-threadedcomments.googlecode.com/svn/trunk/threadedcomments/tests.py