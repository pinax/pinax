=======================================
Robots exclusion application for Django
=======================================

This is a basic Django application to manage robots.txt files following the
`robots exclusion protocol`_, complementing the Django_ `Sitemap contrib app`_.

The robots exclusion application consists of two database models which are
tied together with a m2m relationship:

* Rules_
* URLs_

.. _Django: http://www.djangoproject.com/

Installation
============

Get the source from the application site at::

    http://code.google.com/p/django-robots/

To install the sitemap app, follow these steps:

1. Follow the instructions in the INSTALL.txt file
2. Add ``'robots'`` to your INSTALLED_APPS_ setting.
3. Make sure ``'django.template.loaders.app_directories.load_template_source'``
   is in your TEMPLATE_LOADERS_ setting. It's in there by default, so
   you'll only need to change this if you've changed that setting.
4. Make sure you've installed the `sites framework`_.

.. _INSTALLED_APPS: http://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
.. _TEMPLATE_LOADERS: http://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
.. _sites framework: http://docs.djangoproject.com/en/dev/ref/contrib/sites/

Sitemaps
--------

By default a ``Sitemap`` statement is automatically added to the resulting 
robots.txt by reverse matching the URL of the installed `Sitemap contrib app`_.
This is especially useful if you allow every robot to access your whole site,
since it then gets URLs explicitly instead of searching every link.

To change the default behaviour to omit the inclusion of a sitemap link,
change the ``ROBOTS_USE_SITEMAP`` setting in your Django settings file to::

    ROBOTS_USE_SITEMAP = False

.. _Sitemap contrib app: http://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/

Initialization
==============

To activate robots.txt generation on your Django site, add this line to your
URLconf_::

    (r'^robots.txt$', include('robots.urls')),

This tells Django to build a robots.txt when a robot accesses ``/robots.txt``.
Then, please sync your database to create the necessary tables and create
``Rule`` objects in the admin interface or via the shell.

.. _URLconf: http://docs.djangoproject.com/en/dev/topics/http/urls/
.. _sync your database: http://docs.djangoproject.com/en/dev/ref/django-admin/#syncdb

Rules
=====

``Rule`` - defines an abstract rule which is used to respond to crawling web
robots, using the `robots exclusion protocol`_, a.k.a. robots.txt.

You can link multiple URL pattern to allows or disallows the robot identified
by its user agent to access the given URLs.

The crawl delay field is supported by some search engines and defines the
delay between successive crawler accesses in seconds. If the crawler rate is a
problem for your server, you can set the delay up to 5 or 10 or a comfortable
value for your server, but it's suggested to start with small values (0.5-1),
and increase as needed to an acceptable value for your server. Larger delay
values add more delay between successive crawl accesses and decrease the
maximum crawl rate to your web server.

The `sites framework`_ is used to enable multiple robots.txt per Django instance.
If no rule exists it automatically allows every web robot access to every URL.

Please have a look at the `database of web robots`_ for a full list of
existing web robots user agent strings.

.. _robots exclusion protocol: http://www.robotstxt.org/robotstxt.html
.. _'sites' framework: http://www.djangoproject.com/documentation/sites/
.. _database of web robots: http://www.robotstxt.org/db.html

URLs
====

``Url`` - defines a case-sensitive and exact URL pattern which is used to
allow or disallow the access for web robots. Case-sensitive.

A missing trailing slash does also match files which start with the name of
the given pattern, e.g., ``'/admin'`` matches ``/admin.html`` too.

Some major search engines allow an asterisk (``*``) as a wildcard to match any
sequence of characters and a dollar sign (``$``) to match the end of the URL,
e.g., ``'/*.jpg$'`` can be used to match all jpeg files.

Support
=======

Please leave your `questions and problems`_ on the `designated Google Code site`_.

.. _designated Google Code site: http://code.google.com/p/django-robots/
.. _questions and problems: http://code.google.com/p/django-robots/issues/list
