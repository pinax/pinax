;; Authors: Martin Blais <blais@furius.ca>
;; Date: $Date: 2005/04/01 23:19:41 $
;; Copyright: This module has been placed in the public domain.
;;
;; Regression tests for rst-adjust-section-title.
;; 
;; Run this with::
;;
;;    emacs --script tests-adjust-section.el
;;
;; See test-runner.el for documentation on how the format of tests.


;; Define tests.
(setq rst-adjust-decoration-tests
  '(
;;------------------------------------------------------------------------------
(nodec-first-simple-1
"
Some Title@

"
"
============
 Some Title
============

"
)

;;------------------------------------------------------------------------------
(nodec-first-simple-2
"
Some Title
@
"
"
============
 Some Title
============

"
)

;;------------------------------------------------------------------------------
(nodec-first-simple-3
"
Some Tit@le

"
"
============
 Some Title
============

"
)

;;------------------------------------------------------------------------------
(nodec-first-simple-4
"
@Some Title

"
"
============
 Some Title
============

")


;;------------------------------------------------------------------------------
(nodec-first-simple-others
"
Some Title@

Other Title
-----------

Other Title2
~~~~~~~~~~~~

"
"
============
 Some Title
============

Other Title
-----------

Other Title2
~~~~~~~~~~~~

"
)


;;------------------------------------------------------------------------------
(nodec-first-toggle
"
Some Title@

"
"
Some Title
==========

"
(t))

;;------------------------------------------------------------------------------
(nodec-first-forced
"
   Some Title@

"
"
================
   Some Title
================

"
)

;;------------------------------------------------------------------------------
(nodec-first-forced-2
"
   Some Title@

"
"
Some Title
==========

"
(t))

;;------------------------------------------------------------------------------
(nodec-simple
"
Previous Title
--------------

Some Title@

"
"
Previous Title
--------------

Some Title
~~~~~~~~~~

"
)

;;------------------------------------------------------------------------------
(nodec-simple-neg
"
Previous Title
--------------

Some Title@

Next Title
~~~~~~~~~~

"
"
Previous Title
--------------

Some Title
~~~~~~~~~~

Next Title
~~~~~~~~~~

"
)

;;------------------------------------------------------------------------------
(nodec-simple-toggle
"
Previous Title
--------------

Some Title@

"
"
Previous Title
--------------

~~~~~~~~~~
Some Title
~~~~~~~~~~

"
(t))

;;------------------------------------------------------------------------------
(nodec-simple-force-toggle
"
Previous Title
--------------

  Some Title@

"
"
Previous Title
--------------

~~~~~~~~~~~~~~
  Some Title
~~~~~~~~~~~~~~

"
(t))


;;------------------------------------------------------------------------------
(nodec-simple-forced
"
Previous Title
--------------

   Some Title@

"
"
Previous Title
--------------

Some Title
~~~~~~~~~~

"
)

;;------------------------------------------------------------------------------
(nodec-neg
"
Previous Title
--------------

Some Title@

Next Title
~~~~~~~~~~
"
"
Previous Title
--------------

Some Title
----------

Next Title
~~~~~~~~~~
"
(-1))

;;------------------------------------------------------------------------------
(incomplete-simple-1
"
Previous Title@
----------
"
"
Previous Title
--------------

"
)

;;------------------------------------------------------------------------------
(incomplete-simple-2
"
Previous Title
----------@
"
"
Previous Title
--------------

"
)

;;------------------------------------------------------------------------------
(incomplete-simple-3
"
Previous Title
-@
"
"
================
 Previous Title
================

"
)

;;------------------------------------------------------------------------------
(incomplete-simple-too-long
"
Previous Title
------------------@
"
"
Previous Title
--------------

"
)

;;------------------------------------------------------------------------------
(incomplete-simple-uo
"
----------------
 Previous Title
----------@
"
"
----------------
 Previous Title
----------------

"
)

;;------------------------------------------------------------------------------
(incomplete-partial-overline
"
----------@
 Previous Title
----------------
"
"
----------------
 Previous Title
----------------

"
)

;;------------------------------------------------------------------------------
(incomplete-both
"
----------
 Previous Title@
-----
"
"
----------------
 Previous Title
----------------

"
)

;;------------------------------------------------------------------------------
(incomplete-toggle
"
Previous Title
----------@
"
"
--------------
Previous Title
--------------

"
(t))

;;------------------------------------------------------------------------------
(incomplete-toggle-2
"
----------------
 Previous Title@
--------
"
"
Previous Title
--------------

"
(t))

;;------------------------------------------------------------------------------
(incomplete-toggle-overline
"
--------@
 Previous Title
----------------
"
"
Previous Title
--------------

"
(t))

;;------------------------------------------------------------------------------
(incomplete-top
"--------@
 Previous Title
----------------
"
"----------------
 Previous Title
----------------

"
)

;;------------------------------------------------------------------------------
(incomplete-top-2
"=======
Document Title@
==============
"
"==============
Document Title
==============

"
)

;;------------------------------------------------------------------------------
(complete-simple
"
================
 Document Title
================

SubTitle
--------

My Title@
--------

After Title
~~~~~~~~~~~

"
"
================
 Document Title
================

SubTitle
--------

==========
 My Title
==========

After Title
~~~~~~~~~~~

"
)

;;------------------------------------------------------------------------------
(complete-simple-neg
"
================
 Document Title
================

SubTitle
--------

My Title@
--------

After Title
~~~~~~~~~~~

"
"
================
 Document Title
================

SubTitle
--------

My Title
~~~~~~~~

After Title
~~~~~~~~~~~

"
(-1))

;;------------------------------------------------------------------------------
(complete-simple-suggestion-down
"
================
 Document Title
================

SubTitle
========

My Title@
========

"
"
================
 Document Title
================

SubTitle
========

My Title
--------

"
(-1))

;;------------------------------------------------------------------------------
(complete-simple-boundary-down
"
================
 Document Title
================

SubTitle
========

My Title@
--------

"
"
================
 Document Title
================

SubTitle
========

==========
 My Title
==========

"
(-1))

;;------------------------------------------------------------------------------
(complete-simple-suggestion-up
"
================
 Document Title
================

SubTitle
========

==========
 My Title@
==========

"
"
================
 Document Title
================

SubTitle
========

My Title
--------

"
)

;;------------------------------------------------------------------------------
(complete-simple-boundary-up ;; Note: boundary-up does not exist.
"
================
 Document Title
================

SubTitle
========

My Title@
--------
"
"
================
 Document Title
================

SubTitle
========

My Title
========

"
)

;;------------------------------------------------------------------------------
(complete-toggle-1
"
SubTitle@
~~~~~~~~

"
"
~~~~~~~~~~
 SubTitle
~~~~~~~~~~

"
(t))

;;------------------------------------------------------------------------------
(complete-toggle-2
"
~~~~~~~~~~
 SubTitle@
~~~~~~~~~~

"
"
SubTitle
~~~~~~~~

"
(t))

;;------------------------------------------------------------------------------
(at-file-beginning
"
Document Title@

"
"
================
 Document Title@
================

"
)


;;------------------------------------------------------------------------------
(at-file-ending
"

Document Title@
"
"

================
 Document Title@
================

"
)

;;------------------------------------------------------------------------------
(at-file-ending-2
"

Document Title@"
"

================
 Document Title@
================
"
)

;;------------------------------------------------------------------------------
(conjoint
"
Document Title
==============
Subtitle@

"
"
Document Title
==============
Subtitle@
--------

"
)

;;------------------------------------------------------------------------------
(same-conjoint-2
"==============
Document Title@
==============
Subtitle
========

"
"Document Title@
==============
Subtitle
========

"
)

;;------------------------------------------------------------------------------
(same-conjoint-2b
"
==============
Document Title@
==============
Subtitle
========

"
"
Document Title@
==============
Subtitle
========

"
)


;;------------------------------------------------------------------------------
(same-conjoint-2
"
==============
Document Title
==============
===============
Document Title2@
===============

"
"
==============
Document Title
==============
Document Title2
===============

"
)

;; FIXME: todo
;; ;;------------------------------------------------------------------------------
;; (cycle-previous-only
;; "
;; ==================
;;   Document Title
;; ==================
;; 
;; Document Title2
;; ===============
;; 
;; =======
;;   Bli@
;; =======
;; 
;; Document Title2
;; ===============
;; 
;; Document Title3
;; ---------------
;; 
;; Document Title4
;; ~~~~~~~~~~~~~~~
;; 
;; "
;; "
;; ==================
;;   Document Title
;; ==================
;; 
;; Document Title2
;; ===============
;; 
;; Bli@
;; ---
;; 
;; Document Title2
;; ===============
;; 
;; Document Title3
;; ---------------
;; 
;; Document Title4
;; ~~~~~~~~~~~~~~~
;; 
;; "
;; )

))


;; Main program.  Evaluate this to run the tests.
;; (setq debug-on-error t)

;; Import the module from the file in the parent directory directly.
(add-to-list 'load-path ".")
(load "tests-runner.el")
(add-to-list 'load-path "..")
(load "rst.el")

(progn
  (regression-test-compare-expect-buffer
   "Test interactive adjustment of sections."
   rst-adjust-decoration-tests
   (lambda ()
     (call-interactively 'rst-adjust))
   nil))

