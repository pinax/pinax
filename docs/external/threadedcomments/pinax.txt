======================================
Using django-threadedcomments in Pinax
======================================

While it's perfectly feasible to use the standard threadedcomments templatetags
and views, if you're using django-threadedcomments from within Pinax, it's even
easier.  We've built a small abstraction on top of threadedcomments to build
a standard comment form that integrates with the existing CSS and template
layout.

To use this abstraction layer, in your templates, first make sure to load our
abstraction layer::

    {% load comments_tag %}

Then determine the object on which you would like to comment.  In our example,
it will be a context variable called ``post``.  Now, just include this tag::

    {% comments post %}

And that's it!  Behind the scenes, the ``threadedcomments/comments.html``
template is being loaded and rendered with the following context variables:

``object``:
    The object on which to comment.
    
``request``:
    Django's standard ``request`` object.

``user``:
    The currently logged-in user's ``User`` instance.