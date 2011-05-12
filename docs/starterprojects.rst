.. _starterprojects:

================
Starter Projects
================

One of the core features of Pinax is the inclusion of various starter projects.
There are three very different types of starter project, though, and knowing
the distinction is important to understanding how best to use them.

The three types of Pinax starter project are:

 * foundational
 * demo
 * out-of-the-box

**Foundational projects** are intended to be the starting point for real
projects. They provide the ground-work for you to build on with your
domain-specific apps. Examples of foundational projects are ``zero`` and
``account``.

**Demo projects** are really just intended to showcase particular functionality
and demonstrate how a particular app works or how a set of apps might work
together. You probably wouldn't use them to kick off your projects (other than
to get ideas) and they aren't intended to be used for real sites. Examples of
demo projects are ``social`` and ``sample_group``.

**Out-of-the-box projects** are intended to be useful for real sites with only
minor customization. That is not to say they couldn't be highly modified, but
they don't need to be, beyond things like restyling. Examples of out-of-the-box
projects are ``company`` and ``code``.


Bundled Projects
================

Pinax comes with bundled starter projects which can be used to bootstrap your
project. These starter projects can be used when you run ``setup_project``::

    pinax-admin setup_project -b <project> mysite_project

zero
----

* **Inherits**: Django project layout
* **Type**: foundational

This starter project is what we call Layer Zero. This is not much more than
what you get from ``django-admin startproject``, but follows our conventional
project layout. Here's the directory structure you should see::

    <project-root>
        apps/
            __init__.py
        deploy/
            __init__.py
            fcgi.py
            wsgi.py
        fixtures/
            initial_data.json
        locale/
            ...
        requirements/
            base.txt
            project.txt
        static/
            ...
        templates/
            _footer.html
            homepage.html
            site_base.html
        __init__.py
        manage.py
        settings.py
        urls.py

Our project layout provides you:

 * a home for your apps
 * deployment files
 * initial data (for handling ``sites.Site`` model)
 * project requirements files for use with pip_
 * a home for your site static files (using django-staticfiles_)
 * very simple templates directory

The rest of the files are what you'd expect from Django. They've been modified
to hook up the project infrastructure provided.

Apps included:

 * django-debug-toolbar
 * django-staticfiles
 * django_compressor

.. _pip: http://www.pip-installer.org/
.. _django-staticfiles: http://django-staticfiles.readthedocs.org/

account
-------

 * **Inherits**: zero
 * **Type**: foundational

This starter project builds on zero integrating ``pinax.apps.account`` for
managing user accounts. Users can login, signup, reset password, change email
addresses, change password and change timezone.

Apps included (excluding parent project):

 * pinax.apps.account
 * django-mailer
 * django-email-confirmation
 * django-timezones
 * django-openid
 * django-uni-form

basic
-----

 * **Inherits**: account
 * **Type**: foundational

This starter project adds user profiles and notifications. User profiles
is handled by idios and notifications by django-notification.

Apps included (excluding parent project):

 * django-announcements
 * django-pagination
 * django-notification
 * idios

blog
----

 * **Inherits**: account
 * **Type**: demo

This starter project demos integration of components required to build a blog
site. biblion is used to handle blog posts and dialogos handles comments.

Apps included (excluding parent project):

 * biblion
 * dialogos

static
------

 * **Inherits**: zero
 * **Type**: demo

This project just serves static media and templates with no models or views.
It is a great starting point for doing HTML mockups while taking advantage of
the Django templating language. It uses ``pinax.views.static_view`` mounted
at ``/``. For example if you access ``/test.html`` it will render
``templates/test.html``. Directory paths, i.e., ``/a/``, will render
``/templates/a/index.html``.
