;; Authors: Martin Blais <blais@furius.ca>
;; Date: $Date: 2005/04/01 23:19:41 $
;; Copyright: This module has been placed in the public domain.
;;
;; Simple generic test runner for test scripts.
;;
;; Run this with::
;;
;;    emacs --script <file>.el
;;
;;
;; There are mainly two useful functions from this pacakge:
;;
;; 1. regression-test-compare-expect-values : used to compare expected output
;;    values from running a function;
;;
;; 2. regression-test-compare-expect-buffer : used to compare expected output
;;    buffer contents after running the function.
;;
;; regression-test-compare-expect-values test format
;; -------------------------------------------------
;;
;; The tests are a list of tuples, with the following entries:
;;
;; - a SYMBOL that uniquely identifies the test.
;;
;; - the input buffer CONTENTS to prepare and run the test on.  If char @ is
;;   present in the buffer, it is removed and the cursor is placed at that
;;   position before running the tested function.
;;
;; - the expected OUTPUT value that the function should return.  If the actual
;;   output is different from this, the test will fail.
;;
;; - an optional list of INPUT ARGUMENTS that the test function is called with
;;   for this test.
;; 
;; regression-test-compare-expect-buffer test format
;; -------------------------------------------------
;;
;; - a SYMBOL that uniquely identifies the test.
;;
;; - the input buffer CONTENTS to prepare and run the test on.  Here too, char @
;;   is present in the buffer, it is removed and the cursor is placed at that
;;   position before running the tested function.
;;
;; - the EXPECTED buffer contents after the function has been run.
;;   Additionally, if char @ is present, it is checked that the cursor is
;;   located at that position in the buffer after the function is run (this is
;;   optional).
;;
;; - an optional list of PREFIX ARGUMENTS, which indicates to the test program
;;   to set those prefix arguments before running the given function.  If there
;;   are multiple prefix args, the function is invoked many times.
;;


(require 'cl)

(defvar regression-point-char "@"
  "Special character used to mark the position of point in input
  text and expected text.")

(defun regression-test-loop (suitename testfun testlist fun &optional continue)
  "Loop over a series of tests in a buffer and run the 'testfun'
function."

  (message (format "\n\n   Test Suite: %s\n\n" suitename))

  (let ((buf (get-buffer-create "regression-tests"))
	errtxt
	)
    (dolist (curtest testlist)

      ;; Print current text.
      (message (format "========= %s" (prin1-to-string (car curtest))))

      ;; Prepare a buffer with the starting text, and move the cursor where
      ;; the special character is located.
      (switch-to-buffer buf)
      (erase-buffer)
      (insert (cadr curtest))

      (if (not (search-backward regression-point-char nil t))
	  (error (concat "Error: Badly formed test input, missing "
			 "the cursor position marker.")))

      (delete-char 1)

      (setq errtxt (funcall testfun
			    (car curtest)
			    (caddr curtest)
			    (cadddr curtest)))

      (if errtxt
	  (if continue
	      (progn (message errtxt)
		     (message "(Continuing...)"))
	    (error errtxt)))
    ))
  (message "Done."))


(defun regression-compare-buffers (testname expected testargs)
  "Compare the buffer and expected text and return actual
contents if they do not match."
  
  ;; Run the section title update command n times.
  (dolist (x (or testargs (list nil)))
    (let ((current-prefix-arg x))
      (funcall fun)))

  ;; Compare the buffer output with the expected text.
  (let* (;; Get the actual buffer contents.
	 (actual (buffer-string))
	 ;; Get the expected location of point
	 (exppoint (string-match regression-point-char expected))
	 
	 (expected-clean (if exppoint
			     (concat (substring expected 0 exppoint)
				     (substring expected (+ 1 exppoint)))
			   expected))

	 ;; Adjust position of point vs. string index.
	 (exppoint (and exppoint (+ exppoint 1)))

	 )

    (if (not (string= expected-clean actual))
	;; Error! Test failed.
	(format "Error: Test %s failed: \nexpected\n%s\ngot\n%s"
		testname 
		(prin1-to-string expected-clean) 
		(prin1-to-string actual))
      (if (and exppoint (not (equal exppoint (point))))
	  ;; Error! Test failed, final position of cursor is not the same.
	  (format "Error: Test %s failed: cursor badly placed." testname))
    )))

(defun regression-test-compare-expect-buffer 
  (suitename testlist fun &optional continue)
  "Run the regression tests for the expected buffer contents."
  (regression-test-loop 
   suitename 'regression-compare-buffers testlist fun continue))


(defun regression-compare-values (testname expected testargs)
  "Compare the buffer and expected text and return actual
contents if they do not match."

  (let (actual)
    ;; Run the section title update command n times.
    (setq actual (apply fun testargs))
    
    ;; Compare the buffer output with the expected text.
    (if (not (equal actual expected))
	;; Error! Test failed.
	(format "Error: Test %s failed: expected '%s' got '%s'."
		testname
		(prin1-to-string expected)
		(prin1-to-string actual))
    )))

(defun regression-test-compare-expect-values 
  (suitename testlist fun &optional continue)
  "Run the regression tests for expected values comparison."
  (regression-test-loop 
   suitename 'regression-compare-values testlist fun continue))
