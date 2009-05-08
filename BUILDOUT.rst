==========
 BUILDOUT
==========

POTENTIAL TOOLS
===============

* z3c.recipe.eggbasket : Install eggs from a tarball and create that egg.
* collective.recipe.omelette :	Creates a unified directory structure of all namespace packages, symlinking to the actual contents, in order to ease navigation.
* buildout.eggtractor is a buildout extension that scans the src directory or a list of directories I give for eggs and picks them up automatically. So no more editing of the buildout's configuration file.

BLAH
====

*Maybe* I should have a virtualenv wrapping the buildout: verify
whether or not unwanted python site-packages are available in the
buildout targets (e.g., app_python) or not; we do NOT want them. If
they are available they could interfere with libraries we install via
buildout; if this is true, then why doesn't buildout have some
mechanism to ignore site-packages?

Pinax .tar.gz magic installer fails at startup because it can't find
PIL::

  (pinax-env)chris@Mackeral:mysite$ python manage.py syncdb
  Error: Photologue was unable to import the Python Imaging Library. Please confirm it`s installed and available on your current Python path.

I can install it into the virtualenv with::

  (pinax-env)chris@Mackeral:mysite$ easy_install http://dist.repoze.org/PIL-1.1.6.tar.gz 

but I'd prefer to let a tool like buildout do this for me too; I don't
want to depend on some system having it -- especially if my deploy
system doesn't have all the crap that my development system has.

::

  chris@Mackeral:pinax$ pwd
  /Users/chris/Projects/pinax
  chris@Mackeral:pinax$ /usr/local/python/2.6.1/bin/python bootstrap.py 
  Creating directory '/usr/local/cshenton/Projects/pinax/bin'.
  Creating directory '/usr/local/cshenton/Projects/pinax/parts'.
  Creating directory '/usr/local/cshenton/Projects/pinax/eggs'.
  Creating directory '/usr/local/cshenton/Projects/pinax/develop-eggs'.
  Generated script '/usr/local/cshenton/Projects/pinax/bin/buildout'.
  chris@Mackeral:pinax$ bin/buildout -v
  Installing 'zc.buildout', 'setuptools'.
  ...
  Generated script '/usr/local/cshenton/Projects/pinax/bin/django'.
  Generated script '/usr/local/cshenton/Projects/pinax/bin/test'.
  django: Skipping creating of project: pinax since it exists

