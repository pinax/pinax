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


;; Import the module from the file in the parent directory directly.
(add-to-list 'load-path ".")
(load "tests-runner.el")
(add-to-list 'load-path "..")
(load "rst.el")

;; (setq debug-on-error t)


(setq rst-line-homogeneous-p-tests
  '(
;;------------------------------------------------------------------------------
(simple "Blablabla bla@" nil)
(true "-----------@" ?-)
(indented "   -----------@" ?-)
(letter "aaaa@aaa" ?a)
(true2 "uuuuuuuuuuuuuuuuu@" ?u)
(misleading "--=---------@" nil)
(notstrip " uuuuuuuuuuuuuuuuu@" ?u)
(notstrip2 " uuuuuuuuuuuuuuuuu @" ?u)
(position "-------@----" ?-)
(one-char "-@" nil)
))

(progn
  (regression-test-compare-expect-values
   "Tests for predicate for one char line."
   rst-line-homogeneous-p-tests 'rst-line-homogeneous-p nil))

(setq rst-line-homogeneous-nodent-p-tests
  '(
;;------------------------------------------------------------------------------
(simple "Blablabla bla@" nil)
(true "-----------@" ?-)
(indented "   -----------@" nil)
(letter "aaaa@aaa" ?a)
(true2 "uuuuuuuuuuuuuuuuu@" ?u)
(misleading "--=---------@" nil)
(notstrip " uuuuuuuuuuuuuuuuu@" nil)
(notstrip2 " uuuuuuuuuuuuuuuuu @" nil)
(position "-------@----" ?-)
(one-char "-@" nil)
))

(progn
  (regression-test-compare-expect-values
   "Tests for predicate for one char line."
   rst-line-homogeneous-nodent-p-tests 'rst-line-homogeneous-nodent-p nil))




(setq rst-normalize-cursor-position-tests
      '(
;;------------------------------------------------------------------------------
(under
"

Du bon vin tous les jours.
@
"
"

@Du bon vin tous les jours.

"
)

;;------------------------------------------------------------------------------
(over
"
@
Du bon vin tous les jours.

"
"

@Du bon vin tous les jours.

"
)

;;------------------------------------------------------------------------------
(underline
"

Du bon vin tous les jours.
------@-----
"
"

@Du bon vin tous les jours.
-----------
"
)

;;------------------------------------------------------------------------------
(overline
"
------@-----
Du bon vin tous les jours.

"
"
-----------
@Du bon vin tous les jours.

"
)

;;------------------------------------------------------------------------------
(both
"
@-----------
Du bon vin tous les jours.
-----------

"
"
-----------
@Du bon vin tous les jours.
-----------

"
)

;;------------------------------------------------------------------------------
(joint
"
Du bon vin tous les jours.
@-----------
Du bon vin tous les jours.
-----------

"
"
@Du bon vin tous les jours.
-----------
Du bon vin tous les jours.
-----------

"
)

;;------------------------------------------------------------------------------
(separator
"

@-----------

"
"

@-----------

"
)

;;------------------------------------------------------------------------------
(between
"
Line 1
@
Line 2

"
"
@Line 1

Line 2

"
)

;;------------------------------------------------------------------------------
(between-2
"
=====================================
   Project Idea: Panorama Stitcher
====================================

:Author: Martin Blais <blais@furius.ca>
@
Another Title
=============
"
"
=====================================
   Project Idea: Panorama Stitcher
====================================

@:Author: Martin Blais <blais@furius.ca>

Another Title
=============
"
)

))


(progn
  (regression-test-compare-expect-buffer
   "Test preparation of cursor position."
   rst-normalize-cursor-position-tests 'rst-normalize-cursor-position nil))







(setq rst-get-decoration-tests
      '(
;;------------------------------------------------------------------------------
(nodec-1
"

@Du bon vin tous les jours

"
(nil nil 0))

;;------------------------------------------------------------------------------
(nodec-2
"

@
Du bon vin tous les jours

"
(nil nil 0))

;;------------------------------------------------------------------------------
(nodec-indent
"

@  Du bon vin tous les jours

"
(nil nil 2))

;;------------------------------------------------------------------------------
(underline
"

@Du bon vin tous les jours
=========================

"
(?= simple 0))

;;------------------------------------------------------------------------------
(underline-incomplete
"

@Du bon vin tous les jours
====================

"
(?= simple 0))

;;------------------------------------------------------------------------------
(underline-indent
"

@     Du bon vin tous les jours
====================

"
(?= simple 5))

;;------------------------------------------------------------------------------
(underline-one-char
"

@Du bon vin tous les jours
-
"
(nil nil 0))

;;------------------------------------------------------------------------------
(underline-two-char
"

@Du bon vin tous les jours
--
"
(?- simple 0))

;;------------------------------------------------------------------------------
(over-and-under
"
~~~~~~~~~~~~~~~~~~~~~~~~~
@Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 0))

;;------------------------------------------------------------------------------
(over-and-under-top
"~~~~~~~~~~~~~~~~~~~~~~~~~
@Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 0))

;;------------------------------------------------------------------------------
(over-and-under-indent
"
~~~~~~~~~~~~~~~~~~~~~~~~~
@   Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 3))

;;------------------------------------------------------------------------------
(over-and-under-incomplete
"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 0))

;;------------------------------------------------------------------------------
(over-and-under-different-chars
"
---------------------------
@Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 0))


;;------------------------------------------------------------------------------
(not-beginning
"

Du bon vin to@us les jours
=========================

"
(?= simple 0))

;;------------------------------------------------------------------------------
(over-over-and-under
"
@
=========================
Du bon vin tous les jours
=========================
"
(nil nil 0))

;;------------------------------------------------------------------------------
(joint-1
"
=========================
Du bon vin tous les jours
=========================
Du bon vin@

"
(nil nil 0))

;;------------------------------------------------------------------------------
(joint-2
"
=========================
Du bon vin tous les jours
=========================
Du bon vin@
----------

"
(45 simple 0))

;;------------------------------------------------------------------------------
(joint-3
"
=========================
Du bon vin tous les jours
=========================
----------
Du bon vin@
----------

"
(45 over-and-under 0))

;;------------------------------------------------------------------------------
(joint-4
"
=========================
Du bon vin tous les jours
=========================
--------------
  Du bon vin@
--------------

"
(45 over-and-under 2))

;;------------------------------------------------------------------------------
(indented-1
"

  Du bon vin tous les jours@
  =========================

"
(nil nil 2))

))


(progn
  (regression-test-compare-expect-values
   "Test getting the decoration."
   rst-get-decoration-tests 'rst-get-decoration nil))














(setq text-1
"===============================
   Project Idea: My Document
===============================

:Author: Martin Blais

Introduction
============

This is the introduction.

Notes
-----

Some notes.

Main Points
===========

Yep.

Super Point
-----------

~~~~~~~~~~~
@ Sub Point
~~~~~~~~~~~

Isn't this fabulous?

Conclusion
==========

That's it, really.

")


(setq text-2
"

Previous
--------

Current@
~~~~~~~

Next
++++

")

(setq text-3
"

Previous
--------

Current@
~~~~~~~

  Next
  ++++

")

;; ~~~~~~~~~~~~~~~~~~
;;  Buggy Decoration
;; ~~~~~~
;;
;; ~~~~~~~~~~~~
;;  Decoration
;;
;;
;; ==========

(setq rst-find-all-decorations-tests
      `(
 ;;------------------------------------------------------------------------------
	(basic-1 ,text-1
		 ((2 61 over-and-under 3)
		  (7 61 simple 0)
		  (12 45 simple 0)
		  (17 61 simple 0)
		  (22 45 simple 0)
		  (26 126 over-and-under 1)
		  (31 61 simple 0))
		 )

	(basic-2 ,text-2
		 ((3 45 simple 0)
		  (6 126 simple 0)
		  (9 43 simple 0))
		 )

	(basic-3 ,text-3
		 ((3 45 simple 0)
		  (6 126 simple 0))
		 )

	))


(progn
  (regression-test-compare-expect-values
   "Test finding all the decorations in a file."
   rst-find-all-decorations-tests 'rst-find-all-decorations nil))




(setq rst-get-hierarchy-tests
      `(
 ;;------------------------------------------------------------------------------
	(basic-1 ,text-1
		 ((61 over-and-under 3)
		  (61 simple 0)
		  (45 simple 0)
		  (126 over-and-under 1))
		 )
	))

(progn
  (regression-test-compare-expect-values
   "Test finding the hierarchy of sections in a file."
   rst-get-hierarchy-tests 'rst-get-hierarchy nil))




(setq rst-get-hierarchy-ignore-tests
      `(
 ;;------------------------------------------------------------------------------
	(basic-1 ,text-1
		 ((61 over-and-under 3)
		  (61 simple 0)
		  (45 simple 0))
		 )
	))

(progn
  (regression-test-compare-expect-values
   "Test finding the hierarchy of sections in a file, ignoring lines."
   rst-get-hierarchy-ignore-tests
   (lambda () (rst-get-hierarchy nil (line-number-at-pos))) nil))







(setq rst-decoration-complete-p-tests
  '(
;;------------------------------------------------------------------------------
(nodec
"

@Vaudou

" nil ((?= simple 0)))

;;------------------------------------------------------------------------------
(complete-simple
"
@Vaudou
======
" t ((?= simple 0)))

;;------------------------------------------------------------------------------
(complete-over-and-under
"
======
@Vaudou
======
" t ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(complete-over-and-under-indent
"
==========
@  Vaudou
==========
" t ((?= over-and-under 2)))

;;------------------------------------------------------------------------------
(incomplete-simple-short
"
@Vaudou
=====
" nil ((?= simple 0)))

;;------------------------------------------------------------------------------
(incomplete-simple-long
"
@Vaudou
=======
" nil ((?= simple 0)))

;;------------------------------------------------------------------------------
(incomplete-simple-mixed
"
@Vaudou
===-==
" nil ((?= simple 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-1
"
======
@Vaudou
=====
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-2
"
=====
@Vaudou
======
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-mixed-1
"
======
@Vaudou
===-==
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-mixed-2
"
===-==
@Vaudou
======
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-only
"
======
@Vaudou

" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-mixed
"
======
@Vaudou
------
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-1
"
==========
  @Vaudou
=========
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-2
"
=========
  @Vaudou
==========
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-mixed-1
"
==========
  @Vaudou
===-======
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-and-under-mixed-2
"
===-======
  @Vaudou
==========
" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-over-only
"
==========
  @Vaudou

" nil ((?= over-and-under 0)))

;;------------------------------------------------------------------------------
(incomplete-mixed-2
"
==========
  @Vaudou
----------
" nil ((?= over-and-under 0)))

))

(progn
  (regression-test-compare-expect-values
   "Tests for completeness predicate."
   rst-decoration-complete-p-tests 'rst-decoration-complete-p nil))













(setq rst-get-decorations-around-tests
  '(
;;------------------------------------------------------------------------------
(simple
"

Previous
--------

@Current

Next
++++

" ((?- simple 0) (?+ simple 0)))

;;------------------------------------------------------------------------------
(simple-2
"

Previous
--------

Current@
~~~~~~~

Next
++++

" ((?- simple 0) (?+ simple 0)))

))

(progn
  (regression-test-compare-expect-values
   "Tests getting the decorations around a point."
   rst-get-decorations-around-tests 'rst-get-decorations-around nil))

