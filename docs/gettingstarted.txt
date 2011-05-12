.. _gettingstarted:

===============
Getting started
===============

This guide is designed to point you to the best information about getting
started with Pinax. Pinax is built on top of Python and Django. We leverage
these technologies to their fullest. It is ideal you have some level of
experience with these tools before moving on. Here are some good first
resources if you need to learn about Python and Django:

 * **Python**: `Official Python tutorial`_
 * **Python**: `Dive into Python`_
 * **Django**: `Official Django tutorial`_
 * **Django**: `Official Django documentation`_

Those resources will be excellent reading material if you are not familiar
with Python or Django. The Django tutorial is especially important as many
core Pinax concepts are simply ones you find in Django.

.. _Official Python tutorial: http://docs.python.org/tutorial/
.. _Dive into Python: http://diveintopython.org/
.. _Official Django tutorial: http://docs.djangoproject.com/en/dev/intro/tutorial01/
.. _Official Django documentation: http://docs.djangoproject.com/en/dev/


Prerequisites
=============

To get started with Pinax you must have the following installed:

 * Python 2.4+ — many OSes come with an adequate version of Python. If you are
   on Windows you will need to install it from `python.org`_. Do **not**
   install Python 3+. Pinax is not compatible with Python 3 yet.
 * `virtualenv`_ 1.4.7+
 * `pysqlite`_ — this is only required if you are running **Python 2.4**.
   Later versions of Python have this bundled.
 * :ref:`PIL <ref-pil>` — this is only required if you are using a project
   which requires imaging capabilites (includes projects which support
   avatars and/or photos). It is likely the best idea to install it anyways.

.. _python.org: http://python.org/
.. _pysqlite: http://code.google.com/p/pysqlite/

.. _ref-install:

Installation
============

Pinax highly encourges the use of virtual environments. We will use a tool
called `virtualenv`_ which provides a way to create isolated Python
environments.

Create yourself a virtual environment and activate it::

    $ virtualenv mysite-env
    $ source mysite-env/bin/activate
    (mysite-env)$

If you use Windows this will become::

    $ virtualenv mysite-env
    $ mysite-env\Scripts\activate.bat
    (mysite-env)$

The directory ``mysite-env`` is the environment for your project. It is
recommended you do not edit or create new files/directories within it. The
reason this is important is that this directory should remain reproducible
at all times. Reproducible environments is a good idea.

Notice the ``(mysite-env)`` bit? This is done for you by the ``activate``
script to help you identify which environment is currently activated. Under
the hood your ``PATH`` has been modified to use the Python binary for this
environment.

Go ahead and install Pinax::

    (mysite-env)$ pip install Pinax

.. note:: ``pip install Pinax`` is a development version

    Currently, only our development version is available with pip install.
    Previous versions of Pinax were not available with pip install.
    
    Keep in mind the development version may not be 100% stable. If you are
    looking to help out with development you should read our
    :ref:`development documentation <development>`.

``pip`` you say? pip_ is a tool bundled with virtualenv to install Python
packages. It is super handy and it is used in Pinax extensively to handle
dependencies. You should become very familiar with this tool.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _pip: http://pip.openplans.org/

Pinax is now installed!


Creating a project
==================

Now that Pinax is installed the next step is to create a project. A project is
not much more than a Django project. Pinax provides many more defaults for you
out of the box.

::

    (mysite-env)$ pinax-admin setup_project mysite

This will create a new project named ``mysite``. By default it will install
dependencies for you. You can turn that behavior off by giving ``setup_project``
the ``--no-reqs`` option.

Pinax comes with many different project bases. The default project based is
what we call **layer zero**. It is simply a Django project with some extra
integrated dependencies that will make getting started faster.


Specifying a different project base
-----------------------------------

To see what Pinax has to offer run::

    (mysite-env)$ pinax-admin setup_project -l

This will list all available project bases and a short description about
each. To base your project off of any of these you'd run::

    (mysite-env)$ pinax-admin setup_project -b basic mysite

In many cases the default (``zero``) is enough to get you going, but others
may provide a better starting point for your project.


Running a project
=================

At this point you are now working with Django. Pinax has helped you bootstrap
your project into life. Inside your project you should run::

    (mysite-env)$ python manage.py syncdb
    (mysite-env)$ python manage.py runserver

``syncdb`` will create a SQLite database named ``dev.db`` in your current
directory. We've configured your project to do this, but you can change this
simply by modifying ``settings.py`` where ``DATABASES`` dictionary is
constructed. You can find more information about this at the `get your
database running`_ Django documentation.

``runserver`` runs an embedded webserver to test your site with. By default
it will run on http://localhost:8000. This is configurable and more
information can be found on `runserver in Django documentation`_.

.. _get your database running: http://docs.djangoproject.com/en/dev/topics/install/#get-your-database-running
.. _runserver in Django documentation: http://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-ipaddr-port


What's next?
============

todo
