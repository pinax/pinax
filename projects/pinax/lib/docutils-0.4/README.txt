==================
 README: Docutils
==================

:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Date: $Date: 2005-12-14 18:37:48 +0100 (Wed, 14 Dec 2005) $
:Web site: http://docutils.sourceforge.net/
:Copyright: This document has been placed in the public domain.

.. contents::


Quick-Start
===========

This is for those who want to get up & running quickly.  Read on for
complete details.

1. Get and install the latest release of Python, available from

       http://www.python.org/

   Python 2.2 or later [1]_ is required; Python 2.2.2 or later is
   recommended.

2. Use the latest Docutils code.  Get the code from Subversion or from
   the snapshot:

       http://docutils.sf.net/docutils-snapshot.tgz

   See `Releases & Snapshots`_ below for details.

3. Unpack the tarball in a temporary directory (**not** directly in
   Python's ``site-packages``) and run ``install.py`` with admin
   rights.  On Windows systems it may be sufficient to double-click
   ``install.py``.  On Unix or Mac OS X, type::

        su
        (enter admin password)
        ./install.py

   See Installation_ below for details.

4. Use a front-end tool from the "tools" subdirectory of the same
   directory as in step 3.  For example::

       cd tools
       ./rst2html.py ../FAQ.txt ../FAQ.html        (Unix)
       python rst2html.py ..\FAQ.txt ..\FAQ.html   (Windows)

   See Usage_ below for details.


Purpose
=======

The purpose of the Docutils project is to create a set of tools for
processing plaintext documentation into useful formats, such as HTML,
XML, and LaTeX.  Support for the following sources has been
implemented:

* Standalone files.

* `PEPs (Python Enhancement Proposals)`_.

Support for the following sources is planned:

* Inline documentation from Python modules and packages, extracted
  with namespace context.

* Email (RFC-822 headers, quoted excerpts, signatures, MIME parts).

* Wikis, with global reference lookups of "wiki links".

* Compound documents, such as multiple chapter files merged into a
  book.

* And others as discovered.

.. _PEPs (Python Enhancement Proposals):
   http://www.python.org/peps/pep-0012.html


Releases & Snapshots
====================

While we are trying to follow a "release early & often" policy,
features are added very frequently.  Since the code in the Subversion
repository is usually in a bug-free state, we recommend that you use
the current snapshot (which is usually updated within an hour of
changes being committed to the repository):

* Snapshot of Docutils code, documentation, front-end tools, and
  tests: http://docutils.sf.net/docutils-snapshot.tgz

* Snapshot of the Sandbox (experimental, contributed code):
  http://docutils.sf.net/docutils-sandbox-snapshot.tgz

To keep up to date on the latest developments, download fresh copies
of the snapshots regularly.  New functionality is being added weekly,
sometimes daily.  (There's also the `Subversion repository`_.)

.. _Subversion repository: docs/dev/repository.html


Requirements
============

To run the code, Python 2.2 or later [1]_ must already be installed.
The latest release is recommended.  Python is available from
http://www.python.org/.

The `Python Imaging Library`, or PIL, is used for some image
manipulation operations if it is installed.

.. [1] Python 2.1 may be used providing the compiler package is
   installed.  The compiler package can be found in the Tools/
   directory of Python 2.1's source distribution.

.. _Python Imaging Library: http://www.pythonware.com/products/pil/
.. _Optik: http://optik.sourceforge.net/


Project Files & Directories
===========================

* README.txt: You're reading it.

* COPYING.txt: Public Domain Dedication and copyright details for
  non-public-domain files (most are PD).

* FAQ.txt: Frequently Asked Questions (with answers!).

* RELEASE-NOTES.txt: Summary of the major changes in recent releases.

* HISTORY.txt: A detailed change log, for the current and all previous
  project releases.

* BUGS.txt: Known bugs, and how to report a bug.

* THANKS.txt: List of contributors.

* setup.py: Installation script.  See "Installation" below.

* install.py: Quick & dirty installation script.  Just run it.  For
  any kind of customization or help though, setup.py must be used.

* docutils: The project source directory, installed as a Python
  package.

* extras: Directory for third-party modules that Docutils depends on.
  These are only installed if they're not already present.

* docs: The project documentation directory.  Read ``docs/index.txt``
  for an overview.

* docs/user: The project user documentation directory.  Contains the
  following documents, among others:

  - docs/user/tools.txt: Docutils Front-End Tools
  - docs/user/latex.txt: Docutils LaTeX Writer
  - docs/user/rst/quickstart.txt: A ReStructuredText Primer
  - docs/user/rst/quickref.html: Quick reStructuredText (HTML only)

* docs/ref: The project reference directory.
  ``docs/ref/rst/restructuredtext.txt`` is the reStructuredText
  reference.

* licenses: Directory containing copies of license files for
  non-public-domain files.

* tools: Directory for Docutils front-end tools.  See
  ``docs/user/tools.txt`` for documentation.

* test: Unit tests.  Not required to use the software, but very useful
  if you're planning to modify it.  See `Running the Test Suite`_
  below.


Installation
============

The first step is to expand the ``.tgz`` archive in a temporary
directory (**not** directly in Python's ``site-packages``).  It
contains a distutils setup file "setup.py".  OS-specific installation
instructions follow.


GNU/Linux, BSDs, Unix, Mac OS X, etc.
-------------------------------------

1. Open a shell.

2. Go to the directory created by expanding the archive::

       cd <archive_directory_path>

3. Install the package::

       python setup.py install

   If the python executable isn't on your path, you'll have to specify
   the complete path, such as /usr/local/bin/python.  You may need
   root permissions to complete this step.

   You can also just run install.py; it does the same thing.


Windows
-------

Just double-click ``install.py``.  If this doesn't work, try the
following:

1. Open a DOS Box (Command Shell, MS-DOS Prompt, or whatever they're
   calling it these days).

2. Go to the directory created by expanding the archive::

       cd <archive_directory_path>

3. Install the package::

       <path_to_python.exe>\python setup.py install


Usage
=====

After unpacking and installing the Docutils package, the following
shell commands will generate HTML for all included documentation::

    cd <archive_directory_path>/tools
    ./buildhtml.py ../

On Windows systems, type::

    cd <archive_directory_path>\tools
    python buildhtml.py ..

The final directory name of the ``<archive_directory_path>`` is
"docutils" for snapshots.  For official releases, the directory may be
called "docutils-X.Y.Z", where "X.Y.Z" is the release version.
Alternatively::

    cd <archive_directory_path>
    tools/buildhtml.py --config=tools/docutils.conf          (Unix)
    python tools\buildhtml.py --config=tools\docutils.conf   (Windows)

Some files may generate system messages (warnings and errors).  The
``docs/user/rst/demo.txt`` file (under the archive directory) contains
5 intentional errors.  (They test the error reporting mechanism!)

There are many front-end tools in the unpacked "tools" subdirectory.
You may want to begin with the "rst2html.py" front-end tool.  Most
tools take up to two arguments, the source path and destination path,
with STDIN and STDOUT being the defaults.  Use the "--help" option to
the front-end tools for details on options and arguments.  See
Docutils Front-End Tools (``docs/user/tools.txt``) for full documentation.

The package modules are continually growing and evolving.  The
``docutils.statemachine`` module is usable independently.  It contains
extensive inline documentation (in reStructuredText format of course).

Contributions are welcome!


Running the Test Suite
======================

To run the entire test suite, after installation_ open a shell and use
the following commands::

    cd <archive_directory_path>/test
    ./alltests.py

Under Windows, type::

    cd <archive_directory_path>\test
    python alltests.py

You should see a long line of periods, one for each test, and then a
summary like this::

    Ran 518 tests in 24.653s

    OK
    Elapsed time: 26.189 seconds

The number of tests will grow over time, and the times reported will
depend on the computer running the tests.  The difference between the
two times represents the time required to set up the tests (import
modules, create data structures, etc.).

If any of the tests fail, please `open a bug report`_, `send email`_,
or post a message via the `web interface`_.  Please include all
relevant output, information about your operating system, Python
version, and Docutils version.  To see the Docutils version, use these
commands in the shell::

    cd ../tools
    ./quicktest.py --version

Windows users type these commands::

    cd ..\tools
    python quicktest.py --version

.. _open a bug report:
   http://sourceforge.net/tracker/?group_id=38414&atid=422030
.. _send email: mailto:docutils-users@lists.sourceforge.net
   ?subject=Test%20suite%20failure
.. _web interface: http://post.gmane.org/post.php
   ?group=gmane.text.docutils.user&subject=Test+suite+failure


Getting Help
============

If you have questions or need assistance with Docutils or
reStructuredText, please post a message to the Docutils-users_ mailing
list.

.. _Docutils-users: docs/user/mailing-lists.html#docutils-users


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
