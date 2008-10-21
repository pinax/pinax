=============================================
Tutorial 1
=============================================
Creating a Threaded Comment System for a Blog
---------------------------------------------

Overview
========

Many modern websites have the need for a threaded commenting system.  Places 
like Digg_ and Reddit_ have great systems for responding not only to an item on
the site, but also for responding to comments on that item as well.

.. _Digg: http://www.digg.com/
.. _Reddit: http://www.reddit.com/

*threadedcomments* is a Django application which allows for the simple creation 
of a threaded commenting system.  It is flexible as well, partly due to its use 
of the same facilities that any other Django application would use.  For 
instance, it would be trivial to integrate django-voting_ to rank each comment.  
That, however, is a tutorial for another day.

This tutorial will get you up and running with a threaded comment system for the
typical case: a blog.

.. _django-voting: http://code.google.com/p/django-voting/

Goals of This Tutorial
======================

There are three main goals that this tutorial sets out to meet.  After having
completed this tutorial, you should:

1. Know how to use *threadedcomments* to implement a basic threaded comment 
   system.
2. Have a very good idea on how to integrate this comment system with your blog.

3. Be able to simply and easily migrate an existing ``django.contrib.comments`` 
   installation to use *django_threadedcomments* instead.

Step 1: Defining our Blog Model
===============================

Before we can even begin to use *django_threadedcomments*, we must first create 
a simplistic "blog" model.  This should be very familiar to anyone who has ever 
written a basic blog model in Django before.

We'll define our simplistic blog model as follows::

    from django.db import models
    from datetime import datetime

    class BlogPost(models.Model):
        title = models.CharField(max_length=128)
        slug = models.SlugField(prepopulate_from=('title',))
        body = models.TextField()
        published = models.BooleanField(default=True)
        date_posted = models.DateTimeField(default=datetime.now)

        def __unicode__(self):
            return self.title

        class Admin:
            pass

There shouldn't be anything that's too tricky so far in this ``BlogPost`` model.  
If you're having a hard time understanding what's going on here, you may want to
first check out the `django tutorial`_ or the `django book`_.

If you do understand how this model works, go ahead and use the admin or shell
to create some sample blog posts.  We'll be needing them in the following steps 
of the tutorial.

.. _`django tutorial`: http://www.djangoproject.com/documentation/tutorial01/
.. _`django book`: http://www.djangobook.com/en/1.0/

Step 2: Creating a View for the Sample Blog
===========================================

There are many different choices when it comes to displaying and creating
comments.  Some people choose to show comments in a separate window.  Others
choose to display them on the same page as the content object.  Others still
require users to go to a special comments page to view and create comments.

Our approach here is going to be to display the comments directly below the blog
post, and directly below the comments will be a form for submitting a new 
comment.

Our example will be for the "latest" blog post.  The view is as follows::

    from models import BlogPost
    from django.template import RequestContext
    from django.shortcuts import render_to_response
    from django.http import Http404

    def latest_post(request):
        try:
            post = BlogPost.objects.latest('date_posted')
        except BlogPost.DoesNotExist:
            raise Http404
        return render_to_response(
            'blog/latest_post.html', {'post' : post},
            context_instance = RequestContext(request)
        )

Step 3: Configuration
=====================

First, make sure that django_threadedcomments is installed and is located
somewhere on your pythonpath.  Then, in your ``settings.py`` file, append
the string ``'threadedcomments'`` to the end of your ``INSTALLED_APPS`` tuple.

In the end, your ``INSTALLED_APPS`` should look something like this::

    INSTALLED_APPS = (
        'django.contrib.sessions',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sites',
        'django.contrib.admin',
        'blog',
        'threadedcomments',
    )

Next, make sure that in one of your included url configuration files (preferably
your ``ROOT_URLCONF``) you include 'threadedcomments.urls'.

In the end, your ``urls.py`` file may look something like this::

    from django.conf.urls.defaults import *

    urlpatterns = patterns('',
        (r'^blog/', include('blog.urls')),
        (r'^admin/', include('django.contrib.admin.urls')),
        (r'^threadedcomments/', include('threadedcomments.urls')),
    )

Make sure to run ``python manage.py syncdb`` to finish off this step.

Step 4: Template Creation
=========================

Believe it or not, in this step we're going to not only create a template with
which we can view our latest post, but we're also going to completely integrate
*django_threadedcomments*.  Note also that in our sample template, we are not 
using any of the extremely advisable feature of template inheritance.  The only 
reason that we are not doing so is to simplify the tutorial itself.  In 
practice, please take advantage of this feature.

Now with that said, let's begin to create our template.  We'll start like so::

    {% load threadedcommentstags %}

    <html>
    <head><title>{{ post.title }}</title></head>
    <body>
        <div id="blogpost">
            <h1>{{ post.title }}</h1>
            <h3>Posted On: {{ post.date_posted|date }}</h3>
            {{ post.body|linebreaks }}
        </div>
        <h3>Comments on This Post:</h3>
        {% get_free_threaded_comment_tree for post as tree %}
        {% for comment in tree %}
            <div style="margin-left: {{ comment.depth }}em;" class="comment">
                <a href="{{ comment.website }}">{{ comment.name }}</a> said:<br/>
                {% auto_transform_markup comment %}
            </div>
        {% endfor %}
        <p>Reply to Original:</p>
        <form method="POST" action="{% get_free_comment_url post %}">
            <ul>
                {% get_free_threaded_comment_form as form %}
                {{ form.as_ul }}
                <li><input type="submit" value="Submit Comment" /></li>
            </ul>
        </form>
    </body>
    </html>

There are three main parts to this template:

1. **Displaying the blog post.**

   This part is nothing tricky: the title, date, and body are displayed.

2. **Getting and displaying the comment tree.**

   This part is much more interesting.  A new template tag,
   ``get_free_threaded_comment_tree`` is called on the ``post`` object, and 
   then the results are stored in a context variable called ``tree``.  We 
   iterate over that tree using a simple ``for`` tag and for each comment we 
   provide a link to the commenter's website and display their name.  

   We then call a tag named ``auto_transform_markup`` on the comment.  This  tag
   looks at the markup type and calls the appropriate filter on the body of the 
   post before displaying it.

4. **Providing a form with which the user can reply to the original post.**

   We use ``get_free_threaded_comment_form`` to provide an unbound form to 
   display to the user.  Because of that, we can simply call write 
   ``{{ form.as_ul }}`` and we've got a beautiful, accessible form displayed.

   The ``get_free_comment_url`` template tag gets the appropriate URL to post
   to, given an object.  All appropriate form submissions to that URL will then
   be attached to that given object.  In this case, we want to attach the
   comments to the blog post, so that's the argument that we provide.

There's still a **crucial** piece missing: the ability to reply to other 
people's comments!  This is where some javascript will help us out a lot.

Let's decide on some Javascript functions which will do the trick:

``function show_reply_form(comment_id, url, person_name){ ... }``
    This takes in the ID of the comment for which to add a reply form, the URL 
    to POST to, and the person's name to whom you are replying.
    
    It dynamically inserts into the HTML DOM a FORM element which will POST to 
    the specified URL.

``function hide_reply_form(comment_id, url, person_name){ ... }``
    This takes in the same parameters and instead of dynamically creating a FORM
    element, it dynamically removes the element.

.. note::
    Unfortunately there was not enough space here to display the full Javascript
    functions, but you can view `the full template here`_ to see how one might 
    implement this functionality.

.. _`the full template here`: http://django-threadedcomments.googlecode.com/svn/trunk/examples/tut1/blog/templates/blog/latest_post.html

Now that we've decided on some Javascript functions to create our response 
forms, we'll have to call those functions from our HTML.  We'll do so by adding 
a link directly underneath ``{% auto_transform_markup comment %}``.  It'll look 
like this::

    <a id="c{{ comment.id }}" href="javascript:show_reply_form('c{{ comment.id }}','{% get_free_comment_url post comment %}','{{ comment.name }}')">Reply</a>

That's one long link right there!  What we're doing here is dynamically 
creating a Javascript function call to ``show_reply_form`` using Django's 
context variables as parameters for ``show_reply_form``.  Note that 
``get_free_comment_url`` takes a second argument--the parent comment.  In this
case, we're creating a response form, so the parent comment to the reply will
be the comment that we're currently displaying.  Once Django has processed this 
template, the result will look something like this::

    <a id="c1" href="javascript:show_reply_form('c1','/threadedcomments/freecomment/12/1/1/','Tony Hauber')">Reply</a>

In this case, we're calling ``show_reply_form`` for comment ``c1``, the URL to
POST to is ``/threadedcomments/freecomment/12/1/1/``, and the person's name
that we'd like to respond to is ``Tony Hauber``.

Step 5: Upgrading from ``django.contrib.comments``
==================================================

*django_threadedcomments* provides a simple management command to allow for
the simple upgrading of the built-in ``django.contrib.comments``.  To use it,
simply open a console, navigate to your project directory, and type::

    python manage.py migratecomments

Running this will convert all ``django.contrib.comments.models.Comment`` 
comments to ``threadedcomments.models.ThreadedComment`` comments, and all
``django.contrib.comments.models.FreeComment`` comments to 
``threadedcomments.models.FreeThreadedComment`` comments.

Obviously, there can be no hierarchy data associated with those legacy comments,
but future commenters can reply to those legacy comments just fine.

Wrapping Up
===========

We've finished!  Now it's up to you to style the page according to your wishes,
or even better, apply the techniques from this tutorial on your own blog or web 
application.  For a live example of this, `visit this link`_.  Try it out for 
yourself and even leave comments on that page, if you wish.

.. _`visit this link`: http://www.eflorenzano.com/threadedcomments/example/