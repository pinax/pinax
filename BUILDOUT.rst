==========
 BUILDOUT
==========

:author:	Chris Shenton
:date:		2009-05-11

Intro
=====

The de facto Pinax build process has a couple manual steps but the
bulk of the work is done by the ``pinax-boot.py`` script. The 0.7
series introduced the use of `pip` which installs python parts into
the site-packages directory, presuming a virtualenv to avoid polluting
the system python.

Many folks like using zc.buildout, a generic tool frequently used to
build projects, especially when there are a number of components
involved. It came from the Zope world and is heavily used by the Plone
community for building sites. Rather than installing libraries into
site-packages, interpreters and running systems have their sys.path
set to include all the eggs and libraries and parts as required by the
buildout definitions.

The Django community has typically not been big on using buildout, but
recently Jacob Kaplan-Moss has written a couple tutorials on how to
use it.  I've been using the `djangorecipe` for my builds, like Jacob,
and prefer it for my work.

Pinax has many many components so it seems a natural candidate for
buildout. 

Virtualenv (optional)
=====================

In the bad old days developers installed libraries into the system
Python's site-packages. This of course led to problems akin to "DLL
Hell", with different applications needing different libraries or
versions. 

Virtualenv creates a private copy of your python with its own
site-packages directory so you can install as a normal user and each
project can have it's own set of libraries. 

I tend to install a very minimal set of critical tools into my system
python: setuptools and virtualenv.  All my application's libraries are
installed into the running code's sys.path by buildout, so I don't end
up with conflicts. 

If, however, you do keep a bunch of libraries in your system
site-packages, they will be visible to an application you create with
buildout -- buildout doesn't isolate you from site-packages [why
not?].  It's safest to create a virtual environment::

  virtualenv --no-site-packages .

The dot indicates to create the virtualenv in this current directory,
where our Pinax build will be done. Then activate it::

  source bin/activate

Now when you say "python" it should get your private python.


Building
========

Bootstrap
---------

If you created and activated a virtual python, or want to use the
system one that's on your PATH, bootstrap the buildout::

  $ python bootstrap.py

If you create a private python or need to use a specific one (e.g., a
non-default python version) do something like::

  $ /usr/local/python/2.6/bin/python bootstrap.py

This creates the bin/buildout command used next::

  Creating directory '/usr/local/cshenton/Projects/pinax/bin'.
  Creating directory '/usr/local/cshenton/Projects/pinax/parts'.
  Creating directory '/usr/local/cshenton/Projects/pinax/eggs'.
  Creating directory '/usr/local/cshenton/Projects/pinax/develop-eggs'.
  Generated script '/usr/local/cshenton/Projects/pinax/bin/buildout'.

You should only need to do this once, before you run your buildout.

Buildout
--------

Now you can run the buildout. It uses the configuration `buildout.cfg`
file to drive the build.  You can create layered buildout config files,
like for the project base then variants for development and
deployment, but we'll only worry about a single configuration here.

The buildout.cfg file specifies various parts and dependencies. Run the
buildout with a bit of verbosity like::

  $ bin/buildout -v

  Installing 'zc.buildout', 'setuptools'.
  ...
  Generated script '/usr/local/cshenton/Projects/pinax/bin/django'.
  Generated script '/usr/local/cshenton/Projects/pinax/bin/test'.
  django: Skipping creating of project: pinax since it exists

Since our buildout.cfg specifies a lot of pieces needed by Pinax, this
can take a little time the first time its run. Subsequent times should
take less time. 

I've specified parts in the buildout to build pieces that can be a bit
troublesome, specifically PIL and the zlib that it depends on.

If you don't change things in the buildout.cfg, it will create a
sample application called "mysite" by cloning the Pinax
"social_project".  

When finished, the buildout creates a "bin/pinax" command that's
analogous to Django's django-admin.py.  It also creates a "bin/test"
to run your tests. 

You will need to re-rerun this if you modify the buildout.cfg --
perhaps to add other components your application needs. 


Running
=======

After your buildout completes, you can use the "bin/pinax" commands as
to initialize your database and run your site.

Syncdb
------

At this point you should have the "bin/pinax" command and be able to
create your database from the Pinax models::

  $ bin/pinax syncdb


Runserver
---------

Then you can run your application::

  $ bin/pinax runserver


Test
----

Or run your tests::

  $ bin/test

Python Interpreter
------------------

The buildout also creates a python interpreter that has all the eggs
and libraries configured into it, which you can run like::

  $ bin/pypinax




MISFEATURES
===========

* I'm doing this within Pinax git repo code. I really should do this
  as a separate check-out which has only the bootstrap and
  buildout.cfg.  It would go download the Pinax code by itself.  

* bin/test doesn't work
