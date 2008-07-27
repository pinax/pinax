.. include:: <s5defs.txt>

=============
 Slide Shows
=============

:Author: David Goodger
:Date:   2005-11-28

.. contents::
   :class: handout

.. class:: handout

   This is a test.  This is only a test.  If this were a real slide
   show, there would be a projector handy.

Let's test the S5/HTML writer!

.. class:: small

* Use the arrow keys to navigate.

* Click the "|mode|" button to switch between presentation &
  handout/outline modes.

.. container:: handout

   In presentation mode, mouse over to the lower right-hand corner to
   display the controls.

.. |bullet| unicode:: U+02022
.. |mode| unicode:: U+00D8 .. capital o with stroke
.. footer:: Location |bullet| Date


Introduction
============

.. class:: compact

* reStructuredText

  .. class:: handout

  Uses normal reStructuredText as input.

* One section per slide

  .. class:: handout

  Each first-level section is converted into a single slide.

* (X)HTML output

  .. class:: handout

  Presentations can be viewed using any modern graphical web browser.
  The browser must support CSS, JavaScript, and XHTML.  S5 even works
  with IE!

* Themes

  .. class:: handout

  A variety of themes are available.

* ``rst2s5.py``

  .. class:: handout

  The front-end tool to generate S5 slide shows.


Features (1)
============

.. class:: left

A flush-left paragraph

.. class:: center

A centered paragraph

.. class:: right

A flush-right paragraph

Some colours: :black:`black` [black], :gray:`gray`, :silver:`silver`,
:white:`white` [white], :maroon:`maroon`, :red:`red`,
:magenta:`magenta`, :fuchsia:`fuchsia`, :pink:`pink`,
:orange:`orange`, :yellow:`yellow`, :lime:`lime`, :green:`green`,
:olive:`olive`, :teal:`teal`, :cyan:`cyan`, :aqua:`aqua`,
:blue:`blue`, :navy:`navy`, :purple:`purple`

Features (2)
============

`Some` `incremental` `text.`

.. class:: incremental open

   * :tiny:`tiny` (class & role name: "tiny", e.g. "``:tiny:`text```")
   * :small:`small` ("small")
   * normal (unstyled)
   * :big:`big` ("big")
   * :huge:`huge` ("huge")


Checklist
=========

* The document title should be duplicated on each slide in the footer
  (except for the first slide, ``slide0``, where the entire footer is
  disabled).

* The footer also contains a second line, "Location |bullet| Date"

* There's no table of contents on the first slide, although it does
  appear in the handout/outline.

* Handout material is not displayed in presentation mode.

* The theme directories should be created, and the theme files copied
  over.
