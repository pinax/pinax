;;; ================================================
;;;   rst.el -- ReStructuredText Support for Emacs
;;; ================================================
;;;
;;; :Authors: Martin Blais <blais@furius.ca>,
;;;           Stefan Merten <smerten@oekonux.de>,
;;;           David Goodger <goodger@python.org>
;;; :Revision: $Revision: 4232 $
;;; :Date: $Date: 2005-12-27 14:12:04 +0100 (Tue, 27 Dec 2005) $
;;; :Copyright: This module has been placed in the public domain.
;;; :Abstract:
;;;
;;;    Support code for editing reStructuredText with Emacs.  The latest version
;;;    of this file lies in the docutils source code repository.
;;;
;;; Description
;;; ===========
;;;
;;; Basically, this package contains:
;;;
;;; - Functions to automatically adjust and cycle the section underline
;;;   decorations;
;;; - A mode that displays the table of contents and allows you to jump anywhere
;;;   from it;
;;; - Functions to insert and automatically update a TOC in your source
;;;   document;
;;; - A mode which supports font-lock highlighting of reStructuredText
;;;   structures;
;;; - Some other convenience functions.
;;;
;;; See the accompanying document in the docutils documentation about
;;; the contents of this package and how to use it.
;;;
;;; For more information about reStructuredText, see
;;; http://docutils.sourceforge.net/rst.html
;;;
;;; For full details on how to use the contents of this file, see
;;; http://docutils.sourceforge.net/docs/user/emacs.html
;;;
;;; Download
;;; ========
;;;
;;; Click `Here <rst.el>`_ for download.
;;;
;;; END
;;
;; **IMPORTANT NOTE TO PACKAGERS**: this package is the result of merging:
;;
;; - restructuredtext.el
;; - rst-mode.el
;; - rst-html.el
;;
;; Those files are now OBSOLETE and have been replaced by this single package
;; file (2005-10-30).
;;
;; Installation instructions
;; -------------------------
;;
;; Add this line to your .emacs file and bind the versatile sectioning commands
;; in text mode, like this::
;;
;;   (require 'rst)
;;   (add-hook 'text-mode-hook 'rst-text-mode-bindings)
;;
;; rst-prefix-map is the prefix map for all the functionality provide by this
;; module.  In addition, other shorter bindings are also provided on the
;; mode-specific-map prefix (i.e C-c).
;;
;;
;;    C-c p a (also C-=): rst-adjust
;;
;;       Updates or rotates the section title around point or promotes/demotes
;;       the decorations within the region (see full details below).
;;
;;       Note that C-= is a good binding, since it allows you to specify a
;;       negative arg easily with C-- C-= (easy to type), as well as ordinary
;;       prefix arg with C-u C-=.
;;
;;    C-c p h: rst-display-decorations-hierarchy
;;
;;       Displays the level decorations that are available in the file.
;;
;;    C-c p t: rst-toc
;;
;;       Displays the hierarchical table-of-contents of the document and allows
;;       you to jump to any section from it.
;;
;;    C-c p i: rst-toc-insert
;;
;;       Inserts a table-of-contents in the document at the column where the
;;       cursor is.
;;
;;    C-c p u: rst-toc-insert-update
;;
;;       Find an existing inserted table-of-contents in the document an
;;       updates it.
;;
;;    C-c p p, C-c p n (C-c C-p, C-c C-n): rst-backward-section,
;;    rst-forward-section
;;
;;       Navigate between section titles.
;;
;;    C-c p l, C-c p r (C-c C-l, C-c C-r): rst-shift-region-left,
;;    rst-shift-region-right
;;
;;       Shift the region left or right by two-char increments, which is perfect
;;       for bulleted lists.
;;
;;
;; Other specialized and more generic functions are also available (see source
;; code).  The most important function provided by this file for section title
;; adjustments is rst-adjust.
;;
;; There are many variables that can be customized, look for defcustom and
;; defvar in this file.
;;
;; If you use the table-of-contents feature, you may want to add a hook to
;; update the TOC automatically everytime you adjust a section title::
;;
;;   (add-hook 'rst-adjust-hook 'rst-toc-insert-update)
;;
;; rst-mode
;; --------
;;
;; There is a special mode that you can setup if you want to have syntax
;; highlighting.  The mode is based on `text-mode' and inherits some things from
;; it.  Particularly `text-mode-hook' is run before `rst-mode-hook'.
;;
;; Add the following lines to your `.emacs' file:
;;
;; (setq auto-mode-alist
;;       (append '(("\\.rst$" . rst-mode)
;;                 ("\\.rest$" . rst-mode)) auto-mode-alist))
;;
;; If you are using `.txt' as a standard extension for reST files as
;; http://docutils.sourceforge.net/FAQ.html#what-s-the-standard-filename-extension-for-a-restructuredtext-file
;; suggests you may use one of the `Local Variables in Files' mechanism Emacs
;; provides to set the major mode automatically. For instance you may use
;;
;; .. -*- mode: rst -*-
;;
;; in the very first line of your file. However, because this is a major
;; security breach you or your administrator may have chosen to switch that
;; feature off. See `Local Variables in Files' in the Emacs documentation for a
;; more complete discussion.
;;
;;
;; TODO list
;; =========
;;
;; Bindings
;; --------
;; - We need to automatically add the rst-text-mode-bindings to rst-mode
;; - We need to find better bindings because C-= does not generate an event on
;;   the Macs.
;;
;; rst-toc-insert features
;; ------------------------
;; - rst-toc-insert: We should parse the contents:: options to figure out how
;;   deep to render the inserted TOC.
;; - On load, detect any existing TOCs and set the properties for links.
;; - TOC insertion should have an option to add empty lines.
;; - TOC insertion should deal with multiple lines
;;
;; - There is a bug on redo after undo of adjust when rst-adjust-hook uses the
;;   automatic toc update. The cursor ends up in the TOC and this is
;;   annoying. Gotta fix that.
;;
;; rst-mode
;; --------
;; - Look at the possibility of converting rst-mode from a Major mode to a Minor
;;   mode of text-mode.
;;
;; Other
;; -----
;; - We should rename "adornment" to "decoration" or vice-versa in this
;;   document.
;; - Add an option to forego using the file structure in order to make
;;   suggestion, and to always use the preferred decorations to do that.
;;


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Bindings and hooks

(defgroup rst nil "Support for reStructuredText documents"
  :group 'wp
  :version "21.1"
  :link '(url-link "http://docutils.sourceforge.net/rst.html"))

(defun rst-toc-or-hierarchy ()
  "Binding for either TOC or decorations hierarchy."
  (interactive)
  (if (not current-prefix-arg)
      (rst-toc)
    (rst-display-decorations-hierarchy)))

;; Define a prefix map for the long form of key combinations.
(defvar rst-prefix-map (make-sparse-keymap)
  "Keymap for rst commands.")
(define-key rst-prefix-map "a" 'rst-adjust)
(define-key rst-prefix-map "=" 'rst-adjust)
(define-key rst-prefix-map "t" 'rst-toc)
(define-key rst-prefix-map "h" 'rst-display-decorations-hierarchy)
(define-key rst-prefix-map "i" 'rst-toc-insert)
(define-key rst-prefix-map "+" 'rst-toc-insert)
(define-key rst-prefix-map "p" 'rst-backward-section)
(define-key rst-prefix-map "n" 'rst-forward-section)
(define-key rst-prefix-map "r" 'rst-shift-region-right)
(define-key rst-prefix-map "l" 'rst-shift-region-left)
(define-key rst-prefix-map "u" 'rst-toc-insert-update)
(define-key rst-prefix-map "c" 'rst-compile)
(define-key rst-prefix-map "C" (lambda () (interactive) (rst-compile t)))

(defun rst-text-mode-bindings ()
  "Default text mode hook for rest."

  ;; Direct command (somehow this one does not work on the Mac).
  (local-set-key [(control ?=)] 'rst-adjust)

  (define-key mode-specific-map [(control p)] 'rst-backward-section)
  (define-key mode-specific-map [(control n)] 'rst-forward-section)
  (define-key mode-specific-map [(control r)] 'rst-shift-region-right)
  (define-key mode-specific-map [(control l)] 'rst-shift-region-left)

  ;; Bind the rst commands on the C-c p prefix.
  (define-key mode-specific-map [(p)] rst-prefix-map)
  )


;; Note: we cannot bind the TOC update on file write because it messes with
;; undo.  If we disable undo, since it adds and removes characters, the
;; positions in the undo list are not making sense anymore.  Dunno what to do
;; with this, it would be nice to update when saving.
;;
;; (add-hook 'write-contents-hooks 'rst-toc-insert-update-fun)
;; (defun rst-toc-insert-update-fun ()
;;   ;; Disable undo for the write file hook.
;;   (let ((buffer-undo-list t)) (rst-toc-insert-update) ))


;; Additional abbreviations for text-mode.
(define-abbrev text-mode-abbrev-table
  "con" ".. contents::\n..\n   " nil 0)


;; Paragraph separation customization.  This will work better for
;; bullet and enumerated lists in restructuredtext documents and
;; should not affect filling for other documents too much.  Set it up
;; like this:
;;
;; (add-hook 'text-mode-hook 'rst-set-paragraph-separation)
(defvar rst-extra-paragraph-start
  "\\|[ \t]*\\([-+*] \\|[0-9]+\\. \\)"
  "Extra parapraph-separate patterns to add for text-mode.")
;; FIXME: What about the missing >?
;; The author uses a hardcoded for paragraph-separate: "\f\\|>*[ \t]*$"

(defun rst-set-paragraph-separation ()
  "Sets the paragraph separation for restructuredtext."
  ;; FIXME: the variable should be made automatically buffer local rather than
  ;; using a function here, this function is unnecessary.
  (make-local-variable 'paragraph-start) ; prevent it growing every time
  (setq paragraph-start (concat paragraph-start rst-extra-paragraph-start)))

;; FIXME: What about paragraph-separate?  paragraph-start and paragraph-separate
;; are different.  The author hardcodes the value to
;; "\f\\|>*[ \t]*$\\|>*[ \t]*[-+*] \\|>*[ \t]*[0-9#]+\\. "

;; FIXME: the variables above are in limbo and need some fixing.



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Support functions

(require 'cl)

;; Generic Filter function.
(unless (fboundp 'filter)
  (defun filter (pred list)
    "Returns a list of all the elements fulfilling the pred requirement (that
is for which (pred elem) is true)"
    (if list
	(let ((head (car list))
	      (tail (filter pred (cdr list))))
	  (if (funcall pred head)
	      (cons head tail)
	    tail)))))


;; From emacs-22
(unless (fboundp 'line-number-at-pos)
  (defun line-number-at-pos (&optional pos)
    "Return (narrowed) buffer line number at position POS.
    If POS is nil, use current buffer location."
    (let ((opoint (or pos (point))) start)
      (save-excursion
	(goto-char (point-min))
	(setq start (point))
	(goto-char opoint)
	(forward-line 0)
	(1+ (count-lines start (point)))))) )



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Section Decoration Adjusment
;; ============================
;;
;; The following functions implement a smart automatic title sectioning feature.
;; The idea is that with the cursor sitting on a section title, we try to get as
;; much information from context and try to do the best thing automatically.
;; This function can be invoked many times and/or with prefix argument to rotate
;; between the various sectioning decorations.
;;
;; Definitions: the two forms of sectioning define semantically separate section
;; levels.  A sectioning DECORATION consists in:
;;
;;   - a CHARACTER
;;
;;   - a STYLE which can be either of 'simple' or 'over-and-under'.
;;
;;   - an INDENT (meaningful for the over-and-under style only) which determines
;;     how many characters and over-and-under style is hanging outside of the
;;     title at the beginning and ending.
;;
;; Important note: an existing decoration must be formed by at least two
;; characters to be recognized.
;;
;; Here are two examples of decorations (| represents the window border, column
;; 0):
;;
;;                                  |
;; 1. char: '-'   e                 |Some Title
;;    style: simple                 |----------
;;                                  |
;; 2. char: '='                     |==============
;;    style: over-and-under         |  Some Title
;;    indent: 2                     |==============
;;                                  |
;;
;; Some notes:
;;
;; - The underlining character that is used depends on context. The file is
;;   scanned to find other sections and an appropriate character is selected.
;;   If the function is invoked on a section that is complete, the character is
;;   rotated among the existing section decorations.
;;
;;   Note that when rotating the characters, if we come to the end of the
;;   hierarchy of decorations, the variable rst-preferred-decorations is
;;   consulted to propose a new underline decoration, and if continued, we cycle
;;   the decorations all over again.  Set this variable to nil if you want to
;;   limit the underlining character propositions to the existing decorations in
;;   the file.
;;
;; - A prefix argument can be used to alternate the style.
;;
;; - An underline/overline that is not extended to the column at which it should
;;   be hanging is dubbed INCOMPLETE.  For example::
;;
;;      |Some Title
;;      |-------
;;
;; Examples of default invocation:
;;
;;   |Some Title       --->    |Some Title
;;   |                         |----------
;;
;;   |Some Title       --->    |Some Title
;;   |-----                    |----------
;;
;;   |                         |------------
;;   | Some Title      --->    | Some Title
;;   |                         |------------
;;
;; In over-and-under style, when alternating the style, a variable is
;; available to select how much default indent to use (it can be zero).  Note
;; that if the current section decoration already has an indent, we don't
;; adjust it to the default, we rather use the current indent that is already
;; there for adjustment (unless we cycle, in which case we use the indent
;; that has been found previously).

(defgroup rst-adjust nil
  "Settings for adjustment and cycling of section title
decorations."
  :group 'rst
  :version "21.1")

(defcustom rst-preferred-decorations '( (?= over-and-under 1)
                                         (?= simple 0)
                                         (?- simple 0)
                                         (?~ simple 0)
                                         (?+ simple 0)
                                         (?` simple 0)
                                         (?# simple 0)
                                         (?@ simple 0) )
  "Preferred ordering of section title decorations.  This
  sequence is consulted to offer a new decoration suggestion when
  we rotate the underlines at the end of the existing hierarchy
  of characters, or when there is no existing section title in
  the file."
  :group 'rst-adjust)


(defcustom rst-default-indent 1
  "Number of characters to indent the section title when toggling
  decoration styles.  This is used when switching from a simple
  decoration style to a over-and-under decoration style."
  :group 'rst-adjust)


(defvar rst-section-text-regexp "^[ \t]*\\S-*[a-zA-Z0-9]\\S-*"
  "Regular expression for valid section title text.")


(defun rst-line-homogeneous-p (&optional accept-special)
  "Predicate return the unique char if the current line is
  composed only of a single repeated non-whitespace
  character. This returns the char even if there is whitespace at
  the beginning of the line.

  If ACCEPT-SPECIAL is specified we do not ignore special sequences
  which normally we would ignore when doing a search on many lines.
  For example, normally we have cases to ignore commonly occuring
  patterns, such as :: or ...;  with the flag do not ignore them."
  (save-excursion
    (back-to-indentation)
    (unless (looking-at "\n")
      (let ((c (thing-at-point 'char)))
	(if (and (looking-at (format "[%s]+[ \t]*$" c))
		 (or accept-special
		     (and
		      ;; Common patterns.
		      (not (looking-at "::[ \t]*$"))
		      (not (looking-at "\\.\\.\\.[ \t]*$"))
		      ;; Discard one char line
		      (not (looking-at ".[ \t]*$"))
		      )))
	    (string-to-char c))
	))
    ))

(defun rst-line-homogeneous-nodent-p (&optional accept-special)
  (save-excursion
    (beginning-of-line)
    (if (looking-at "^[ \t]+")
        nil
      (rst-line-homogeneous-p accept-special)
      )))


(defun rst-compare-decorations (deco1 deco2)
  "Compare decorations.  Returns true if both are equal,
according to restructured text semantics (only the character and
the style are compared, the indentation does not matter."
  (and (eq (car deco1) (car deco2))
       (eq (cadr deco1) (cadr deco2))))


(defun rst-get-decoration-match (hier deco)
  "Returns the index (level) of the decoration in the given hierarchy.
This basically just searches for the item using the appropriate
comparison and returns the index.  We return nil if the item is
not found."
  (let ((cur hier))
    (while (and cur (not (rst-compare-decorations (car cur) deco)))
      (setq cur (cdr cur)))
    cur))


(defun rst-suggest-new-decoration (alldecos &optional prev)
  "Suggest a new, different decoration, different from all that
have been seen.

  ALLDECOS is the set of all decorations, including the line
  numbers.  PREV is the optional previous decoration, in order to
  suggest a better match."

  ;; For all the preferred decorations...
  (let* (
         ;; If 'prev' is given, reorder the list to start searching after the
         ;; match.
         (fplist
          (cdr (rst-get-decoration-match rst-preferred-decorations prev)))

         ;; List of candidates to search.
         (curpotential (append fplist rst-preferred-decorations)))
    (while
        ;; For all the decorations...
        (let ((cur alldecos)
              found)
          (while (and cur (not found))
            (if (rst-compare-decorations (car cur) (car curpotential))
                ;; Found it!
                (setq found (car curpotential))
              (setq cur (cdr cur))))
          found)

      (setq curpotential (cdr curpotential)))

    (copy-list (car curpotential)) ))

(defun rst-delete-line ()
  "A version of kill-line that does not use the kill-ring."
  (delete-region (line-beginning-position) (min (+ 1 (line-end-position))
						(point-max))))

(defun rst-update-section (char style &optional indent)
  "Unconditionally updates the style of a section decoration
  using the given character CHAR, with STYLE 'simple or
  'over-and-under, and with indent INDENT.  If the STYLE is
  'simple, whitespace before the title is removed (indent is
  always assume to be 0).

  If there are existing overline and/or underline from the
  existing decoration, they are removed before adding the
  requested decoration."

  (interactive)
  (let (marker
        len
        ec
        (c ?-))

      (end-of-line)
      (setq marker (point-marker))

      ;; Fixup whitespace at the beginning and end of the line
      (if (or (null indent) (eq style 'simple))
          (setq indent 0))
      (beginning-of-line)
      (delete-horizontal-space)
      (insert (make-string indent ? ))

      (end-of-line)
      (delete-horizontal-space)

      ;; Set the current column, we're at the end of the title line
      (setq len (+ (current-column) indent))

      ;; Remove previous line if it consists only of a single repeated character
      (save-excursion
        (forward-line -1)
        (and (rst-line-homogeneous-p 1)
             ;; Avoid removing the underline of a title right above us.
             (save-excursion (forward-line -1)
                             (not (looking-at rst-section-text-regexp)))
             (rst-delete-line)))

      ;; Remove following line if it consists only of a single repeated
      ;; character
      (save-excursion
        (forward-line +1)
        (and (rst-line-homogeneous-p 1)
             (rst-delete-line))
        ;; Add a newline if we're at the end of the buffer, for the subsequence
        ;; inserting of the underline
        (if (= (point) (buffer-end 1))
            (newline 1)))

      ;; Insert overline
      (if (eq style 'over-and-under)
          (save-excursion
            (beginning-of-line)
            (open-line 1)
            (insert (make-string len char))))

      ;; Insert underline
      (forward-line +1)
      (open-line 1)
      (insert (make-string len char))

      (forward-line +1)
      (goto-char marker)
      ))


(defun rst-normalize-cursor-position ()
  "If the cursor is on a decoration line or an empty line , place
  it on the section title line (at the end).  Returns the line
  offset by which the cursor was moved. This works both over or
  under a line."
  (if (save-excursion (beginning-of-line)
                      (or (rst-line-homogeneous-p 1)
                          (looking-at "^[ \t]*$")))
      (progn
        (beginning-of-line)
        (cond
         ((save-excursion (forward-line -1)
                          (beginning-of-line)
                          (and (looking-at rst-section-text-regexp)
                               (not (rst-line-homogeneous-p 1))))
          (progn (forward-line -1) -1))
         ((save-excursion (forward-line +1)
                          (beginning-of-line)
                          (and (looking-at rst-section-text-regexp)
                               (not (rst-line-homogeneous-p 1))))
          (progn (forward-line +1) +1))
         (t 0)))
    0 ))


(defun rst-find-all-decorations ()
  "Finds all the decorations in the file, and returns a list of
  (line, decoration) pairs.  Each decoration consists in a (char,
  style, indent) triple.

  This function does not detect the hierarchy of decorations, it
  just finds all of them in a file.  You can then invoke another
  function to remove redundancies and inconsistencies."

  (let (positions
        (curline 1))
    ;; Iterate over all the section titles/decorations in the file.
    (save-excursion
      (beginning-of-buffer)
      (while (< (point) (buffer-end 1))
        (if (rst-line-homogeneous-nodent-p)
            (progn
              (setq curline (+ curline (rst-normalize-cursor-position)))

              ;; Here we have found a potential site for a decoration,
              ;; characterize it.
              (let ((deco (rst-get-decoration)))
                (if (cadr deco) ;; Style is existing.
                    ;; Found a real decoration site.
                    (progn
                      (push (cons curline deco) positions)
                      ;; Push beyond the underline.
                      (forward-line 1)
                      (setq curline (+ curline 1))
                      )))
              ))
        (forward-line 1)
        (setq curline (+ curline 1))
        ))
    (reverse positions)))


(defun rst-infer-hierarchy (decorations)
  "Build a hierarchy of decorations using the list of given decorations.

  This function expects a list of (char, style, indent)
  decoration specifications, in order that they appear in a file,
  and will infer a hierarchy of section levels by removing
  decorations that have already been seen in a forward traversal of the
  decorations, comparing just the character and style.

  Similarly returns a list of (char, style, indent), where each
  list element should be unique."

  (let ((hierarchy-alist (list)))
    (dolist (x decorations)
      (let ((char (car x))
            (style (cadr x))
            (indent (caddr x)))
        (unless (assoc (cons char style) hierarchy-alist)
	  (setq hierarchy-alist
		(append hierarchy-alist
			(list (cons (cons char style) x)))) )
        ))
    (mapcar 'cdr hierarchy-alist)
    ))


(defun rst-get-hierarchy (&optional alldecos ignore)
  "Returns a list of decorations that represents the hierarchy of
  section titles in the file.

  If the line number in IGNORE is specified, the decoration found
  on that line (if there is one) is not taken into account when
  building the hierarchy."
  (let ((all (or alldecos (rst-find-all-decorations))))
    (setq all (assq-delete-all ignore all))
    (rst-infer-hierarchy (mapcar 'cdr all))))


(defun rst-get-decoration (&optional point)
  "Looks around point and finds the characteristics of the
  decoration that is found there.  We assume that the cursor is
  already placed on the title line (and not on the overline or
  underline).

  This function returns a (char, style, indent) triple.  If the
  characters of overline and underline are different, we return
  the underline character.  The indent is always calculated.  A
  decoration can be said to exist if the style is not nil.

  A point can be specified to go to the given location before
  extracting the decoration."

  (let (char style indent)
    (save-excursion
      (if point (goto-char point))
      (beginning-of-line)
      (if (looking-at rst-section-text-regexp)
          (let* ((over (save-excursion
                         (forward-line -1)
                         (rst-line-homogeneous-nodent-p)))

                (under (save-excursion
                         (forward-line +1)
                         (rst-line-homogeneous-nodent-p)))
                )

            ;; Check that the line above the overline is not part of a title
            ;; above it.
            (if (and over
                     (save-excursion
                       (and (equal (forward-line -2) 0)
                            (looking-at rst-section-text-regexp))))
                (setq over nil))

            (cond
             ;; No decoration found, leave all return values nil.
             ((and (eq over nil) (eq under nil)))

             ;; Overline only, leave all return values nil.
             ;;
             ;; Note: we don't return the overline character, but it could
             ;; perhaps in some cases be used to do something.
             ((and over (eq under nil)))

             ;; Underline only.
             ((and under (eq over nil))
              (setq char under
                    style 'simple))

             ;; Both overline and underline.
             (t
              (setq char under
                    style 'over-and-under))
             )
            )
        )
      ;; Find indentation.
      (setq indent (save-excursion (back-to-indentation) (current-column)))
      )
    ;; Return values.
    (list char style indent)))


(defun rst-get-decorations-around (&optional alldecos)
  "Given the list of all decorations (with positions),
find the decorations before and after the given point.
A list of the previous and next decorations is returned."
  (let* ((all (or alldecos (rst-find-all-decorations)))
         (curline (line-number-at-pos))
         prev next
         (cur all))

    ;; Search for the decorations around the current line.
    (while (and cur (< (caar cur) curline))
      (setq prev cur
            cur (cdr cur)))
    ;; 'cur' is the following decoration.

    (if (and cur (caar cur))
        (setq next (if (= curline (caar cur)) (cdr cur) cur)))

    (mapcar 'cdar (list prev next))
    ))


(defun rst-decoration-complete-p (deco &optional point)
  "Return true if the decoration DECO around POINT is complete."
  ;; Note: we assume that the detection of the overline as being the underline
  ;; of a preceding title has already been detected, and has been eliminated
  ;; from the decoration that is given to us.

  ;; There is some sectioning already present, so check if the current
  ;; sectioning is complete and correct.
  (let* ((char (car deco))
         (style (cadr deco))
         (indent (caddr deco))
         (endcol (save-excursion (end-of-line) (current-column)))
         )
    (if char
        (let ((exps (concat "^"
                            (regexp-quote (make-string (+ endcol indent) char))
                            "$")))
          (and
           (save-excursion (forward-line +1)
                           (beginning-of-line)
                           (looking-at exps))
           (or (not (eq style 'over-and-under))
               (save-excursion (forward-line -1)
                               (beginning-of-line)
                               (looking-at exps))))
          ))
    ))


(defun rst-get-next-decoration
  (curdeco hier &optional suggestion reverse-direction)
  "Get the next decoration for CURDECO, in given hierarchy HIER,
and suggesting for new decoration SUGGESTION."

  (let* (
         (char (car curdeco))
         (style (cadr curdeco))

         ;; Build a new list of decorations for the rotation.
         (rotdecos
          (append hier
                  ;; Suggest a new decoration.
                  (list suggestion
                        ;; If nothing to suggest, use first decoration.
                        (car hier)))) )
    (or
     ;; Search for next decoration.
     (cadr
      (let ((cur (if reverse-direction rotdecos
                   (reverse rotdecos)))
            found)
        (while (and cur
                    (not (and (eq char (caar cur))
                              (eq style (cadar cur)))))
          (setq cur (cdr cur)))
        cur))

     ;; If not found, take the first of all decorations.
     suggestion
     )))


(defun rst-adjust ()
  "Adjust/rotate the section decoration for the section title
around point or promote/demote the decorations inside the region,
depending on if the region is active.  This function is meant to
be invoked possibly multiple times, and can vary its behaviour
with a positive prefix argument (toggle style), or with a
negative prefix argument (alternate behaviour).

This function is the main focus of this module and is a bit of a
swiss knife.  It is meant as the single most essential function
to be bound to invoke to adjust the decorations of a section
title in restructuredtext.  It tries to deal with all the
possible cases gracefully and to do `the right thing' in all
cases.

See the documentations of rst-adjust-decoration and
rst-promote-region for full details.

Prefix Arguments
================

The method can take either (but not both) of

a. a (non-negative) prefix argument, which means to toggle the
   decoration style.  Invoke with C-u prefix for example;

b. a negative numerical argument, which generally inverts the
   direction of search in the file or hierarchy.  Invoke with C--
   prefix for example.

"
  (interactive)

  (let* ( ;; Parse the positive and negative prefix arguments.
         (reverse-direction
          (and current-prefix-arg
               (< (prefix-numeric-value current-prefix-arg) 0)))
         (toggle-style
          (and current-prefix-arg (not reverse-direction))))

    (if (and transient-mark-mode mark-active)
        ;; Adjust decorations within region.
        (rst-promote-region current-prefix-arg)
      ;; Adjust decoration around point.
      (rst-adjust-decoration toggle-style reverse-direction))

    ;; Run the hooks to run after adjusting.
    (run-hooks 'rst-adjust-hook)

    ))

(defvar rst-adjust-hook nil
  "Hooks to be run after running rst-adjust.")

(defun rst-adjust-decoration (&optional toggle-style reverse-direction)
"Adjust/rotate the section decoration for the section title around point.

This function is meant to be invoked possibly multiple times, and
can vary its behaviour with a true TOGGLE-STYLE argument, or with
a REVERSE-DIRECTION argument.

General Behaviour
=================

The next action it takes depends on context around the point, and
it is meant to be invoked possibly more than once to rotate among
the various possibilities. Basically, this function deals with:

- adding a decoration if the title does not have one;

- adjusting the length of the underline characters to fit a
  modified title;

- rotating the decoration in the set of already existing
  sectioning decorations used in the file;

- switching between simple and over-and-under styles.

You should normally not have to read all the following, just
invoke the method and it will do the most obvious thing that you
would expect.


Decoration Definitions
======================

The decorations consist in

1. a CHARACTER

2. a STYLE which can be either of 'simple' or 'over-and-under'.

3. an INDENT (meaningful for the over-and-under style only)
   which determines how many characters and over-and-under
   style is hanging outside of the title at the beginning and
   ending.

See source code for mode details.


Detailed Behaviour Description
==============================

Here are the gory details of the algorithm (it seems quite
complicated, but really, it does the most obvious thing in all
the particular cases):

Before applying the decoration change, the cursor is placed on
the closest line that could contain a section title.

Case 1: No Decoration
---------------------

If the current line has no decoration around it,

- search backwards for the last previous decoration, and apply
  the decoration one level lower to the current line.  If there
  is no defined level below this previous decoration, we suggest
  the most appropriate of the rst-preferred-decorations.

  If REVERSE-DIRECTION is true, we simply use the previous
  decoration found directly.

- if there is no decoration found in the given direction, we use
  the first of rst-preferred-decorations.

The prefix argument forces a toggle of the prescribed decoration
style.

Case 2: Incomplete Decoration
-----------------------------

If the current line does have an existing decoration, but the
decoration is incomplete, that is, the underline/overline does
not extend to exactly the end of the title line (it is either too
short or too long), we simply extend the length of the
underlines/overlines to fit exactly the section title.

If the prefix argument is given, we toggle the style of the
decoration as well.

REVERSE-DIRECTION has no effect in this case.

Case 3: Complete Existing Decoration
------------------------------------

If the decoration is complete (i.e. the underline (overline)
length is already adjusted to the end of the title line), we
search/parse the file to establish the hierarchy of all the
decorations (making sure not to include the decoration around
point), and we rotate the current title's decoration from within
that list (by default, going *down* the hierarchy that is present
in the file, i.e. to a lower section level).  This is meant to be
used potentially multiple times, until the desired decoration is
found around the title.

If we hit the boundary of the hierarchy, exactly one choice from
the list of preferred decorations is suggested/chosen, the first
of those decoration that has not been seen in the file yet (and
not including the decoration around point), and the next
invocation rolls over to the other end of the hierarchy (i.e. it
cycles).  This allows you to avoid having to set which character
to use by always using the

If REVERSE-DIRECTION is true, the effect is to change the
direction of rotation in the hierarchy of decorations, thus
instead going *up* the hierarchy.

However, if there is a non-negative prefix argument, we do not
rotate the decoration, but instead simply toggle the style of the
current decoration (this should be the most common way to toggle
the style of an existing complete decoration).


Point Location
==============

The invocation of this function can be carried out anywhere
within the section title line, on an existing underline or
overline, as well as on an empty line following a section title.
This is meant to be as convenient as possible.


Indented Sections
=================

Indented section titles such as ::

   My Title
   --------

are illegal in restructuredtext and thus not recognized by the
parser.  This code will thus not work in a way that would support
indented sections (it would be ambiguous anyway).


Joint Sections
==============

Section titles that are right next to each other may not be
treated well.  More work might be needed to support those, and
special conditions on the completeness of existing decorations
might be required to make it non-ambiguous.

For now we assume that the decorations are disjoint, that is,
there is at least a single line between the titles/decoration
lines.


Suggested Binding
=================

We suggest that you bind this function on C-=.  It is close to
C-- so a negative argument can be easily specified with a flick
of the right hand fingers and the binding is unused in text-mode."
  (interactive)

  ;; If we were invoked directly, parse the prefix arguments into the
  ;; arguments of the function.
  (if current-prefix-arg
      (setq reverse-direction
            (and current-prefix-arg
                 (< (prefix-numeric-value current-prefix-arg) 0))

            toggle-style
            (and current-prefix-arg (not reverse-direction))))

  (let* (;; Check if we're on an underline around a section title, and move the
         ;; cursor to the title if this is the case.
         (moved (rst-normalize-cursor-position))

         ;; Find the decoration and completeness around point.
         (curdeco (rst-get-decoration))
         (char (car curdeco))
         (style (cadr curdeco))
         (indent (caddr curdeco))

         ;; New values to be computed.
         char-new style-new indent-new
         )

    ;; We've moved the cursor... if we're not looking at some text, we have
    ;; nothing to do.
    (if (save-excursion (beginning-of-line)
                        (looking-at rst-section-text-regexp))
        (progn
          (cond
           ;;-------------------------------------------------------------------
           ;; Case 1: No Decoration
           ((and (eq char nil) (eq style nil))

            (let* ((alldecos (rst-find-all-decorations))

                   (around (rst-get-decorations-around alldecos))
                   (prev (car around))
                   cur

                   (hier (rst-get-hierarchy alldecos))
                   )

              ;; Advance one level down.
              (setq cur
                    (if prev
                        (if (not reverse-direction)
                            (or (cadr (rst-get-decoration-match hier prev))
                                (rst-suggest-new-decoration hier prev))
                          prev)
                      (copy-list (car rst-preferred-decorations))
                      ))

              ;; Invert the style if requested.
              (if toggle-style
                  (setcar (cdr cur) (if (eq (cadr cur) 'simple)
                                        'over-and-under 'simple)) )

              (setq char-new (car cur)
                    style-new (cadr cur)
                    indent-new (caddr cur))
              ))

           ;;-------------------------------------------------------------------
           ;; Case 2: Incomplete Decoration
           ((not (rst-decoration-complete-p curdeco))

            ;; Invert the style if requested.
            (if toggle-style
                (setq style (if (eq style 'simple) 'over-and-under 'simple)))

            (setq char-new char
                  style-new style
                  indent-new indent))

           ;;-------------------------------------------------------------------
           ;; Case 3: Complete Existing Decoration
           (t
            (if toggle-style

                ;; Simply switch the style of the current decoration.
                (setq char-new char
                      style-new (if (eq style 'simple) 'over-and-under 'simple)
                      indent-new rst-default-indent)

              ;; Else, we rotate, ignoring the decoration around the current
              ;; line...
              (let* ((alldecos (rst-find-all-decorations))

                     (hier (rst-get-hierarchy alldecos (line-number-at-pos)))

                     ;; Suggestion, in case we need to come up with something
                     ;; new
                     (suggestion (rst-suggest-new-decoration
                                  hier
                                  (car (rst-get-decorations-around alldecos))))

                     (nextdeco (rst-get-next-decoration
                                curdeco hier suggestion reverse-direction))

                     )

                ;; Indent, if present, always overrides the prescribed indent.
                (setq char-new (car nextdeco)
                      style-new (cadr nextdeco)
                      indent-new (caddr nextdeco))

                )))
           )

          ;; Override indent with present indent!
          (setq indent-new (if (> indent 0) indent indent-new))

          (if (and char-new style-new)
              (rst-update-section char-new style-new indent-new))
          ))


    ;; Correct the position of the cursor to more accurately reflect where it
    ;; was located when the function was invoked.
    (unless (= moved 0)
      (forward-line (- moved))
      (end-of-line))

    ))

;; Maintain an alias for compatibility.
(defalias 'rst-adjust-section-title 'rst-adjust)


(defun rst-promote-region (&optional demote)
  "Promote the section titles within the region.

With argument DEMOTE or a prefix argument, demote the
section titles instead.  The algorithm used at the boundaries of
the hierarchy is similar to that used by rst-adjust-decoration."
  (interactive)

  (let* ((demote (or current-prefix-arg demote))
         (alldecos (rst-find-all-decorations))
         (cur alldecos)

         (hier (rst-get-hierarchy alldecos))
         (suggestion (rst-suggest-new-decoration hier))

         (region-begin-line (line-number-at-pos (region-beginning)))
         (region-end-line (line-number-at-pos (region-end)))

         marker-list
         )

    ;; Skip the markers that come before the region beginning
    (while (and cur (< (caar cur) region-begin-line))
      (setq cur (cdr cur)))

    ;; Create a list of markers for all the decorations which are found within
    ;; the region.
    (save-excursion
      (let (m line)
        (while (and cur (< (setq line (caar cur)) region-end-line))
          (setq m (make-marker))
          (goto-line line)
          (push (list (set-marker m (point)) (cdar cur)) marker-list)
          (setq cur (cdr cur)) ))

      ;; Apply modifications.
      (let (nextdeco)
        (dolist (p marker-list)
          ;; Go to the decoration to promote.
          (goto-char (car p))

          ;; Rotate the next decoration.
          (setq nextdeco (rst-get-next-decoration
                          (cadr p) hier suggestion demote))

          ;; Update the decoration.
          (apply 'rst-update-section nextdeco)

          ;; Clear marker to avoid slowing down the editing after we're done.
          (set-marker (car p) nil)
          ))
      (setq deactivate-mark nil)
    )))



(defun rst-display-decorations-hierarchy (&optional decorations)
  "Display the current file's section title decorations hierarchy.
  This function expects a list of (char, style, indent) triples."
  (interactive)

  (if (not decorations)
      (setq decorations (rst-get-hierarchy)))
  (with-output-to-temp-buffer "*rest section hierarchy*"
    (let ((level 1))
      (with-current-buffer standard-output
        (dolist (x decorations)
          (insert (format "\nSection Level %d" level))
          (apply 'rst-update-section x)
          (end-of-buffer)
          (insert "\n")
          (incf level)
          ))
    )))


(defun rst-rstrip (str)
  "Strips the whitespace at the end of a string."
  (let ((tmp))
    (string-match "[ \t\n]*\\'" str)
    (substring str 0 (match-beginning 0))
    ))

(defun rst-get-stripped-line ()
  "Returns the line at cursor, stripped from whitespace."
  (re-search-forward "\\S-.*\\S-" (line-end-position))
  (buffer-substring-no-properties (match-beginning 0)
                                  (match-end 0)) )

(defun rst-section-tree (alldecos)
  "Returns a hierarchical tree of the sections titles in the
document.  This can be used to generate a table of contents for
the document.  The top node will always be a nil node, with the
top-level titles as children (there may potentially be more than
one).

Each section title consists in a cons of the stripped title
string and a marker to the section in the original text document.

If there are missing section levels, the section titles are
inserted automatically, and the title string is set to nil, and
the marker set to the first non-nil child of itself.
Conceptually, the nil nodes--i.e. those which have no title--are
to be considered as being the same line as their first non-nil
child.  This has advantages later in processing the graph."

  (let* (thelist
         (hier (rst-get-hierarchy alldecos))
         (levels (make-hash-table :test 'equal :size 10))
         lines)

    (let ((lev 0))
      (dolist (deco hier)
	;; Compare just the character and indent in the hash table.
        (puthash (cons (car deco) (cadr deco)) lev levels)
        (incf lev)))

    ;; Create a list of lines that contains (text, level, marker) for each
    ;; decoration.
    (save-excursion
      (setq lines
            (mapcar (lambda (deco)
                      (goto-line (car deco))
                      (list (gethash (cons (cadr deco) (caddr deco)) levels)
                            (rst-get-stripped-line)
                            (let ((m (make-marker)))
                              (beginning-of-line 1)
                              (set-marker m (point)))
                            ))
                    alldecos)))

    (let ((lcontnr (cons nil lines)))
      (rst-section-tree-rec lcontnr -1))))


(defun rst-section-tree-rec (decos lev)
  "Recursive function for the implementation of the section tree
  building. DECOS is a cons cell whose cdr is the remaining list
  of decorations, and we change it as we consume them.  LEV is
  the current level of that node.  This function returns a pair
  of the subtree that was built.  This treats the decos list
  destructively."

  (let ((ndeco (cadr decos))
        node
        children)

    ;; If the next decoration matches our level
    (when (and ndeco (= (car ndeco) lev))
      ;; Pop the next decoration and create the current node with it
      (setcdr decos (cddr decos))
      (setq node (cdr ndeco)) )
    ;; Else we let the node title/marker be unset.

    ;; Build the child nodes
    (while (and (cdr decos) (> (caadr decos) lev))
      (setq children
            (cons (rst-section-tree-rec decos (1+ lev))
                  children)))
    (setq children (reverse children))

    ;; If node is still unset, we use the marker of the first child.
    (when (eq node nil)
      (setq node (cons nil (cdaar children))))

    ;; Return this node with its children.
    (cons node children)
    ))


(defun rst-section-tree-point (node &optional point)
  "Given a computed and valid section tree SECTREE and a point
  POINT (default being the current point in the current buffer),
  find and return the node within the sectree where the cursor
  lives.

  Return values: a pair of (parent path, container subtree).  The
  parent path is simply a list of the nodes above the container
  subtree node that we're returning."

  (let (path outtree)

    (let* ((curpoint (or point (point))))

      ;; Check if we are before the current node.
      (if (and (cadar node) (>= curpoint (cadar node)))

	  ;; Iterate all the children, looking for one that might contain the
	  ;; current section.
	  (let ((curnode (cdr node))
		last)

	    (while (and curnode (>= curpoint (cadaar curnode)))
	      (setq last curnode
		    curnode (cdr curnode)))

	    (if last
		(let ((sub (rst-section-tree-point (car last) curpoint)))
		  (setq path (car sub)
			outtree (cdr sub)))
	      (setq outtree node))

	    )))
    (cons (cons (car node) path) outtree)
    ))


(defun rst-toc-insert (&optional pfxarg)
  "Insert a simple text rendering of the table of contents.
By default the top level is ignored if there is only one, because
we assume that the document will have a single title.

If a numeric prefix argument is given, insert the TOC up to the
specified level.

The TOC is inserted indented at the current column."

  (interactive "P")

  (let* (;; Check maximum level override
         (rst-toc-insert-max-level
          (if (and (integerp pfxarg) (> (prefix-numeric-value pfxarg) 0))
              (prefix-numeric-value pfxarg) rst-toc-insert-max-level))

         ;; Get the section tree for the current cursor point.
         (sectree-pair
	  (rst-section-tree-point
	   (rst-section-tree (rst-find-all-decorations))))

         ;; Figure out initial indent.
         (initial-indent (make-string (current-column) ? ))
         (init-point (point)))

    (when (cddr sectree-pair)
      (rst-toc-insert-node (cdr sectree-pair) 0 initial-indent "")

      ;; Fixup for the first line.
      (delete-region init-point (+ init-point (length initial-indent)))

      ;; Delete the last newline added.
      (delete-backward-char 1)
    )))


(defgroup rst-toc nil
  "Settings for reStructuredText table of contents."
  :group 'rst
  :version "21.1")

(defcustom rst-toc-indent 2
  "Indentation for table-of-contents display (also used for
  formatting insertion, when numbering is disabled)."
  :group 'rst-toc)

(defcustom rst-toc-insert-style 'fixed
  "Set this to one of the following values to determine numbering and
indentation style:
- plain: no numbering (fixed indentation)
- fixed: numbering, but fixed indentation
- aligned: numbering, titles aligned under each other
- listed: numbering, with dashes like list items (EXPERIMENTAL)
"
  :group 'rst-toc)

(defcustom rst-toc-insert-number-separator "  "
  "Separator that goes between the TOC number and the title."
  :group 'rst-toc)

;; This is used to avoid having to change the user's mode.
(defvar rst-toc-insert-click-keymap
  (let ((map (make-sparse-keymap)))
       (define-key map [mouse-1] 'rst-toc-mode-mouse-goto)
       map)
  "(Internal) What happens when you click on propertized text in the TOC.")

(defcustom rst-toc-insert-max-level nil
  "If non-nil, maximum depth of the inserted TOC."
  :group 'rst-toc)

(defun rst-toc-insert-node (node level indent pfx)
  "Recursive function that does the print of the inserted
toc. PFX is the prefix numbering, that includes the alignment
necessary for all the children of this level to align."

  ;; Note: we do child numbering from the parent, so we start number the
  ;; children one level before we print them.
  (let ((do-print (> level 0))
        (count 1)
        b)
    (when do-print
      (insert indent)
      (let ((b (point)))
	(unless (equal rst-toc-insert-style 'plain)
	  (insert pfx rst-toc-insert-number-separator))
	(insert (or (caar node) "[missing node]"))
	;; Add properties to the text, even though in normal text mode it
	;; won't be doing anything for now.  Not sure that I want to change
	;; mode stuff.  At least the highlighting gives the idea that this
	;; is generated automatically.
	(put-text-property b (point) 'mouse-face 'highlight)
	(put-text-property b (point) 'rst-toc-target (cadar node))
	(put-text-property b (point) 'keymap rst-toc-insert-click-keymap)

	)
      (insert "\n")

      ;; Prepare indent for children.
      (setq indent
	    (cond
	     ((eq rst-toc-insert-style 'plain)
	      (concat indent rst-toc-indent))

	     ((eq rst-toc-insert-style 'fixed)
	      (concat indent (make-string rst-toc-indent ? )))

	     ((eq rst-toc-insert-style 'aligned)
	      (concat indent (make-string (+ (length pfx) 2) ? )))

	     ((eq rst-toc-insert-style 'listed)
	      (concat (substring indent 0 -3)
		      (concat (make-string (+ (length pfx) 2) ? ) " - ")))
	     ))
      )

    (if (or (eq rst-toc-insert-max-level nil)
            (< level rst-toc-insert-max-level))
        (let ((do-child-numbering (>= level 0))
              fmt)
          (if do-child-numbering
              (progn
                ;; Add a separating dot if there is already a prefix
                (if (> (length pfx) 0)
                    (setq pfx (concat (rst-rstrip pfx) ".")))

                ;; Calculate the amount of space that the prefix will require
                ;; for the numbers.
                (if (cdr node)
                    (setq fmt (format "%%-%dd"
                                      (1+ (floor (log10 (length
							 (cdr node))))))))
                ))

          (dolist (child (cdr node))
            (rst-toc-insert-node child
				 (1+ level)
				 indent
				 (if do-child-numbering
				     (concat pfx (format fmt count)) pfx))
            (incf count)))

      )))


(defun rst-toc-insert-find-delete-contents ()
  "Finds and deletes an existing comment after the first contents directive and
delete that region. Return t if found and the cursor is left after the comment."
  (goto-char (point-min))
  ;; We look for the following and the following only (in other words, if your
  ;; syntax differs, this won't work.  If you would like a more flexible thing,
  ;; contact the author, I just can't imagine that this requirement is
  ;; unreasonable for now).
  ;;
  ;;   .. contents:: [...anything here...]
  ;;   ..
  ;;      XXXXXXXX
  ;;      XXXXXXXX
  ;;      [more lines]
  ;;
  (let ((beg
         (re-search-forward "^\\.\\. contents[ \t]*::\\(.*\\)\n\\.\\."
                            nil t))
        last-real)
    (when beg
      ;; Look for the first line that starts at the first column.
      (forward-line 1)
      (beginning-of-line)
      (while (and
	      (< (point) (point-max))
	      (or (and (looking-at "[ \t]+[^ \t]") (setq last-real (point)) t)
		  (looking-at "\\s-*$")))
	(forward-line 1)
        )
      (if last-real
          (progn
            (goto-char last-real)
            (end-of-line)
            (delete-region beg (point)))
        (goto-char beg))
      t
      )))

(defun rst-toc-insert-update ()
  "Automatically find the .. contents:: section of a document and update the
inserted TOC if present.  You can use this in your file-write hook to always
make it up-to-date automatically."
  (interactive)
  (save-excursion
    (if (rst-toc-insert-find-delete-contents)
        (progn (insert "\n    ")
               (rst-toc-insert))) )
  ;; Note: always return nil, because this may be used as a hook.
  )


;;------------------------------------------------------------------------------

(defun rst-toc-node (node level)
  "Recursive function that does the print of the TOC in rst-toc-mode."

  (if (> level 0)
      (let ((b (point)))
        ;; Insert line text.
        (insert (make-string (* rst-toc-indent (1- level)) ? ))
        (insert (or (caar node) "[missing node]"))

        ;; Highlight lines.
        (put-text-property b (point) 'mouse-face 'highlight)

        ;; Add link on lines.
        (put-text-property b (point) 'rst-toc-target (cadar node))

        (insert "\n")
	))

  (dolist (child (cdr node))
    (rst-toc-node child (1+ level))))

(defun rst-toc-count-lines (node target-node)
  "Count the number of lines to the TARGET-NODE node.  This
recursive function returns a cons of the number of additional
lines that have been counted for its node and children and 't if
the node has been found."

  (let ((count 1)
	found)
    (if (eq node target-node)
	(setq found t)
      (let ((child (cdr node)))
	(while (and child (not found))
	  (let ((cl (rst-toc-count-lines (car child) target-node)))
	    (setq count (+ count (car cl))
		  found (cdr cl)
		  child (cdr child))))))
    (cons count found)))


(defun rst-toc ()
  "Finds all the section titles and their decorations in the
  file, and displays a hierarchically-organized list of the
  titles, which is essentially a table-of-contents of the
  document.

  The emacs buffer can be navigated, and selecting a section
  brings the cursor in that section."
  (interactive)
  (let* ((curbuf (current-buffer))

         ;; Get the section tree
         (alldecos (rst-find-all-decorations))
         (sectree (rst-section-tree alldecos))

 	 (our-node (cdr (rst-section-tree-point sectree)))
	 line

         ;; Create a temporary buffer.
         (buf (get-buffer-create rst-toc-buffer-name))
         )

    (with-current-buffer buf
      (let ((inhibit-read-only t))
        (rst-toc-mode)
        (delete-region (point-min) (point-max))
        (insert (format "Table of Contents: %s\n" (or (caar sectree) "")))
        (put-text-property (point-min) (point)
                           'face (list '(background-color . "lightgray")))
        (rst-toc-node sectree 0)

	;; Count the lines to our found node.
	(let ((linefound (rst-toc-count-lines sectree our-node)))
	  (setq line (if (cdr linefound) (car linefound) 0)))
        ))
    (display-buffer buf)
    (pop-to-buffer buf)

    ;; Save the buffer to return to.
    (set (make-local-variable 'rst-toc-return-buffer) curbuf)

    ;; Move the cursor near the right section in the TOC.
    (goto-line line)
    ))


(defun rst-toc-mode-find-section ()
  (let ((pos (get-text-property (point) 'rst-toc-target)))
    (unless pos
      (error "No section on this line"))
    (unless (buffer-live-p (marker-buffer pos))
      (error "Buffer for this section was killed"))
    pos))

(defvar rst-toc-buffer-name "*Table of Contents*"
  "Name of the Table of Contents buffer.")

(defun rst-toc-mode-goto-section ()
  "Go to the section the current line describes."
  (interactive)
  (let ((pos (rst-toc-mode-find-section)))
    (kill-buffer (get-buffer rst-toc-buffer-name))
    (pop-to-buffer (marker-buffer pos))
    (goto-char pos)
    (recenter 5)))

(defun rst-toc-mode-mouse-goto (event)
  "In Rst-Toc mode, go to the occurrence whose line you click on."
  (interactive "e")
  (let (pos)
    (save-excursion
      (set-buffer (window-buffer (posn-window (event-end event))))
      (save-excursion
        (goto-char (posn-point (event-end event)))
        (setq pos (rst-toc-mode-find-section))))
    (pop-to-buffer (marker-buffer pos))
    (goto-char pos)))

(defun rst-toc-mode-mouse-goto-kill (event)
  (interactive "e")
  (call-interactively 'rst-toc-mode-mouse-goto event)
  (kill-buffer (get-buffer rst-toc-buffer-name)))

(defvar rst-toc-return-buffer nil
  "Buffer local variable that is used to return to the original
  buffer from the TOC.")

(defun rst-toc-quit-window ()
  (interactive)
  (quit-window)
  (pop-to-buffer rst-toc-return-buffer))

(defvar rst-toc-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map [mouse-1] 'rst-toc-mode-mouse-goto-kill)
    (define-key map [mouse-2] 'rst-toc-mode-mouse-goto)
    (define-key map "\C-m" 'rst-toc-mode-goto-section)
    (define-key map "f" 'rst-toc-mode-goto-section)
    (define-key map "q" 'rst-toc-quit-window)
    (define-key map "z" 'kill-this-buffer)
    map)
  "Keymap for `rst-toc-mode'.")

(put 'rst-toc-mode 'mode-class 'special)

(defun rst-toc-mode ()
  "Major mode for output from \\[rst-toc]."
  (interactive)
  (kill-all-local-variables)
  (use-local-map rst-toc-mode-map)
  (setq major-mode 'rst-toc-mode)
  (setq mode-name "Rst-TOC")
  (setq buffer-read-only t)
  )

;; Note: use occur-mode (replace.el) as a good example to complete missing
;; features.


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Section movement commands.
;;

(defun rst-forward-section (&optional offset)
  "Skip to the next restructured text section title.
  OFFSET specifies how many titles to skip.  Use a negative OFFSET to move
  backwards in the file (default is to use 1)."
  (interactive)
  (let* (;; Default value for offset.
         (offset (or offset 1))

         ;; Get all the decorations in the file, with their line numbers.
         (alldecos (rst-find-all-decorations))

         ;; Get the current line.
         (curline (line-number-at-pos))

         (cur alldecos)
         (idx 0)
         line
         )

    ;; Find the index of the "next" decoration w.r.t. to the current line.
    (while (and cur (< (caar cur) curline))
      (setq cur (cdr cur))
      (incf idx))
    ;; 'cur' is the decoration on or following the current line.

    (if (and (> offset 0) cur (= (caar cur) curline))
        (incf idx))

    ;; Find the final index.
    (setq idx (+ idx (if (> offset 0) (- offset 1) offset)))
    (setq cur (nth idx alldecos))

    ;; If the index is positive, goto the line, otherwise go to the buffer
    ;; boundaries.
    (if (and cur (>= idx 0))
        (goto-line (car cur))
      (if (> offset 0) (end-of-buffer) (beginning-of-buffer)))
    ))

(defun rst-backward-section ()
  "Like rst-forward-section, except move back one title."
  (interactive)
  (rst-forward-section -1))




;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Functions to indent/dedent item lists, which are always two-characters apart
;; horizontally with rest.

(defvar rst-shift-fill-region nil
  "Set to true if you want to automatically re-fill the region that is being
shifted.")
;; FIXME: need to finish this feature properly.


(defun rst-shift-region-right ()
  "Indent region ridigly, by two characters to the right."
  (interactive)
  (let ((mbeg (set-marker (make-marker) (region-beginning)))
	(mend (set-marker (make-marker) (region-end))))
    (indent-rigidly mbeg mend 2)
    (when rst-shift-fill-region
      (fill-region mbeg mend))
    ))

(defun rst-find-leftmost-column (beg end)
  "Finds the leftmost column in the region."
  (let ((mincol 1000))
    (save-excursion
      (goto-char beg)
      (while (< (point) end)
        (back-to-indentation)
        (unless (looking-at "[ \t]*$")
	  (setq mincol (min mincol (current-column))))
        (forward-line 1)
        ))
    mincol))

(defun rst-shift-region-left (pfxarg)
  "Indent region ridigly, by two characters to the left.
If invoked with a prefix arg, the entire indentation is removed,
up to the leftmost character in the region."
  (interactive "P")
  (let ((chars
         (if pfxarg
             (- (rst-find-leftmost-column (region-beginning) (region-end)))
           -2))
	(mbeg (set-marker (make-marker) (region-beginning)))
	(mend (set-marker (make-marker) (region-end)))
	)
    (indent-rigidly mbeg mend chars)
    (when rst-shift-fill-region
      (fill-region mbeg mend))
    ))



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; rst-mode.el --- Mode for viewing and editing reStructuredText-documents.
;;
;; Copyright 2003 Stefan Merten <smerten@oekonux.de>
;;
;; Note: this is an update from version 0.2.9 of rst-mode.el
;;
;; DESCRIPTION
;;
;; This package provides support for documents marked up using the
;; reStructuredText format. Support includes font locking as well as some
;; convenience functions for editing. It does this by defining a Emacs major
;; mode.
;;
;; The package is based on text-mode and inherits some things from it.
;; Particularly text-mode-hook is run before rst-mode-hook.
;;
;; OPTIONS
;;
;; There are a number of things which can be customized using the standard
;; Emacs customization features. There are two customization groups for this
;; mode.
;;
;; Customization
;; =============
;;
;; rst
;; ---
;; This group contains some general customizable features.
;;
;; The group is contained in the wp group.
;;
;; rst-faces
;; ---------
;; This group contains all necessary for customizing fonts. The default
;; settings use standard font-lock-*-face's so if you set these to your
;; liking they are probably good in rst-mode also.
;;
;; The group is contained in the faces group as well as in the rst group.
;;
;; rst-faces-defaults
;; ------------------
;; This group contains all necessary for customizing the default fonts used for
;; section title faces.
;;
;; The general idea for section title faces is to have a non-default background
;; but do not change the background. The section level is shown by the
;; lightness of the background color. If you like this general idea of
;; generating faces for section titles but do not like the details this group
;; is the point where you can customize the details. If you do not like the
;; general idea, however, you should customize the faces used in
;; rst-adornment-faces-alist.
;;
;; Note: If you are using a dark background please make sure the variable
;; frame-background-mode is set to the symbol dark. This triggers
;; some default values which are probably right for you.
;;
;; The group is contained in the rst-faces group.
;;
;; All customizable features have a comment explaining their meaning. Refer to
;; the customization of your Emacs (try ``M-x customize``).

;; SEE ALSO
;;
;; http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html

;; AUTHOR
;;
;; Stefan Merten <smerten AT oekonux.de>

;; LICENSE
;;
;; This program is licensed under the terms of the GPL. See
;;
;;   http://www.gnu.org/licenses/gpl.txt

;; AVAILABILITY
;;
;; See
;;
;;   http://www.merten-home.de/FreeSoftware/rst-mode/


;;; Code:

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Customization:

(defcustom rst-mode-hook nil
  "Hook run when Rst Mode is turned on. The hook for Text Mode is run before
  this one."
  :group 'rst
  :type '(hook))

(defcustom rst-mode-lazy t
  "*If non-nil Rst Mode font-locks comment, literal blocks, and section titles
correctly. Because this is really slow it switches on Lazy Lock Mode
automatically. You may increase Lazy Lock Defer Time for reasonable results.

If nil comments and literal blocks are font-locked only on the line they start.

The value of this variable is used when Rst Mode is turned on."
  :group 'rst
  :type '(boolean))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defgroup rst-faces nil "Faces used in Rst Mode"
  :group 'rst
  :group 'faces
  :version "21.1")

(defcustom rst-block-face 'font-lock-keyword-face
  "All syntax marking up a special block"
  :group 'rst-faces
  :type '(face))

(defcustom rst-external-face 'font-lock-type-face
  "Field names and interpreted text"
  :group 'rst-faces
  :type '(face))

(defcustom rst-definition-face 'font-lock-function-name-face
  "All other defining constructs"
  :group 'rst-faces
  :type '(face))

(defcustom rst-directive-face
  ;; XEmacs compatibility
  (if (boundp 'font-lock-builtin-face)
      'font-lock-builtin-face
    'font-lock-preprocessor-face)
  "Directives and roles"
  :group 'rst-faces
  :type '(face))

(defcustom rst-comment-face 'font-lock-comment-face
  "Comments"
  :group 'rst-faces
  :type '(face))

(defcustom rst-emphasis1-face
  ;; XEmacs compatibility
  (if (facep 'italic)
      ''italic
    'italic)
  "Simple emphasis"
  :group 'rst-faces
  :type '(face))

(defcustom rst-emphasis2-face
  ;; XEmacs compatibility
  (if (facep 'bold)
      ''bold
    'bold)
  "Double emphasis"
  :group 'rst-faces
  :type '(face))

(defcustom rst-literal-face 'font-lock-string-face
  "Literal text"
  :group 'rst-faces
  :type '(face))

(defcustom rst-reference-face 'font-lock-variable-name-face
  "References to a definition"
  :group 'rst-faces
  :type '(face))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defgroup rst-faces-defaults nil
  "Values used to generate default faces for section titles on all levels.
Tweak these if you are content with how section title faces are built in
general but you do not like the details."
  :group 'rst-faces
  :version "21.1")

(defun rst-define-level-faces ()
  "Define the faces for the section title text faces from the values."
  ;; All variables used here must be checked in `rst-set-level-default'
  (let ((i 1))
    (while (<= i rst-level-face-max)
      (let ((sym (intern (format "rst-level-%d-face" i)))
	    (doc (format "Face for showing section title text at level %d" i))
	    (col (format (concat "%s" rst-level-face-format-light)
			 rst-level-face-base-color
			 (+ (* (1- i) rst-level-face-step-light)
			    rst-level-face-base-light))))
	(make-empty-face sym)
	(set-face-doc-string sym doc)
	(set-face-background sym col)
	(set sym sym)
	(setq i (1+ i))))))

(defun rst-set-level-default (sym val)
  "Set a customized value affecting section title text face and recompute the
faces."
  (custom-set-default sym val)
  ;; Also defines the faces initially when all values are available
  (and (boundp 'rst-level-face-max)
       (boundp 'rst-level-face-format-light)
       (boundp 'rst-level-face-base-color)
       (boundp 'rst-level-face-step-light)
       (boundp 'rst-level-face-base-light)
       (rst-define-level-faces)))

;; Faces for displaying items on several levels; these definitions define
;; different shades of grey where the lightest one (i.e. least contrasting) is
;; used for level 1
(defcustom rst-level-face-max 6
  "Maximum depth of levels for which section title faces are defined."
  :group 'rst-faces-defaults
  :type '(integer)
  :set 'rst-set-level-default)
(defcustom rst-level-face-base-color "grey"
  "The base name of the color to be used for creating background colors in
ection title faces for all levels."
  :group 'rst-faces-defaults
  :type '(string)
  :set 'rst-set-level-default)
(defcustom rst-level-face-base-light
  (if (eq frame-background-mode 'dark)
      15
    85)
  "The lightness factor for the base color. This value is used for level 1. The
default depends on whether the value of `frame-background-mode' is `dark' or
not."
  :group 'rst-faces-defaults
  :type '(integer)
  :set 'rst-set-level-default)
(defcustom rst-level-face-format-light "%2d"
  "The format for the lightness factor appended to the base name of the color.
This value is expanded by `format' with an integer."
  :group 'rst-faces-defaults
  :type '(string)
  :set 'rst-set-level-default)
(defcustom rst-level-face-step-light
  (if (eq frame-background-mode 'dark)
      7
    -7)
  "The step width to use for the next color. The formula

    `rst-level-face-base-light'
    + (`rst-level-face-max' - 1) * `rst-level-face-step-light'

must result in a color level which appended to `rst-level-face-base-color'
using `rst-level-face-format-light' results in a valid color such as `grey50'.
This color is used as background for section title text on level
`rst-level-face-max'."
  :group 'rst-faces-defaults
  :type '(integer)
  :set 'rst-set-level-default)

(defcustom rst-adornment-faces-alist
  (let ((alist '((t . font-lock-keyword-face)
		 (nil . font-lock-keyword-face)))
	(i 1))
    (while (<= i rst-level-face-max)
      (nconc alist (list (cons i (intern (format "rst-level-%d-face" i)))))
      (setq i (1+ i)))
    alist)
  "Provides faces for the various adornment types. Key is a number (for the
section title text of that level), t (for transitions) or nil (for section
title adornment). If you generally do not like how section title text faces are
set up tweak here. If the general idea is ok for you but you do not like the
details check the Rst Faces Defaults group."
  :group 'rst-faces
  :type '(alist
	  :key-type
	  (choice
	   (integer
	    :tag
	    "Section level (may not be bigger than `rst-level-face-max')")
	   (boolean :tag "transitions (on) / section title adornment (off)"))
	  :value-type (face))
  :set-after '(rst-level-face-max))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; FIXME: Code from `restructuredtext.el' should be integrated

(defvar rst-mode-syntax-table nil
  "Syntax table used while in rst mode.")

(unless rst-mode-syntax-table
  (setq rst-mode-syntax-table (make-syntax-table text-mode-syntax-table))
  (modify-syntax-entry ?$ "." rst-mode-syntax-table)
  (modify-syntax-entry ?% "." rst-mode-syntax-table)
  (modify-syntax-entry ?& "." rst-mode-syntax-table)
  (modify-syntax-entry ?' "." rst-mode-syntax-table)
  (modify-syntax-entry ?* "." rst-mode-syntax-table)
  (modify-syntax-entry ?+ "." rst-mode-syntax-table)
  (modify-syntax-entry ?. "_" rst-mode-syntax-table)
  (modify-syntax-entry ?/ "." rst-mode-syntax-table)
  (modify-syntax-entry ?< "." rst-mode-syntax-table)
  (modify-syntax-entry ?= "." rst-mode-syntax-table)
  (modify-syntax-entry ?> "." rst-mode-syntax-table)
  (modify-syntax-entry ?\\ "\\" rst-mode-syntax-table)
  (modify-syntax-entry ?| "." rst-mode-syntax-table)
  (modify-syntax-entry ?_ "." rst-mode-syntax-table)
  )

(defvar rst-mode-abbrev-table nil
 "Abbrev table used while in rst mode.")
(define-abbrev-table 'rst-mode-abbrev-table ())

;; FIXME: Movement keys to skip forward / backward over or mark an indented
;; block could be defined; keys to markup section titles based on
;; `rst-adornment-level-alist' would be useful
(defvar rst-mode-map nil
  "Keymap for rst mode. This inherits from Text mode.")

(unless rst-mode-map
  (setq rst-mode-map (copy-keymap text-mode-map)))

(defun rst-mode ()
  "Major mode for editing reStructuredText documents.

You may customize `rst-mode-lazy' to switch font-locking of blocks.

\\{rst-mode-map}
Turning on `rst-mode' calls the normal hooks `text-mode-hook' and
`rst-mode-hook'."
  (interactive)
  (kill-all-local-variables)

  ;; Maps and tables
  (use-local-map rst-mode-map)
  (setq local-abbrev-table rst-mode-abbrev-table)
  (set-syntax-table rst-mode-syntax-table)

  ;; For editing text
  ;;
  ;; FIXME: It would be better if this matches more exactly the start of a reST
  ;; paragraph; however, this not always possible with a simple regex because
  ;; paragraphs are determined by indentation of the following line
  (set (make-local-variable 'paragraph-start)
       (concat page-delimiter "\\|[ \t]*$"))
  (if (eq ?^ (aref paragraph-start 0))
      (setq paragraph-start (substring paragraph-start 1)))
  (set (make-local-variable 'paragraph-separate) paragraph-start)
  (set (make-local-variable 'indent-line-function) 'indent-relative-maybe)
  (set (make-local-variable 'adaptive-fill-mode) t)
  (set (make-local-variable 'comment-start) ".. ")

  ;; Special variables
  (make-local-variable 'rst-adornment-level-alist)

  ;; Font lock
  (set (make-local-variable 'font-lock-defaults)
       '(rst-font-lock-keywords-function
	 t nil nil nil
	 (font-lock-multiline . t)
	 (font-lock-mark-block-function . mark-paragraph)))
  (when (boundp 'font-lock-support-mode)
    ;; rst-mode has its own mind about font-lock-support-mode
    (make-local-variable 'font-lock-support-mode)
    (cond
     ((and (not rst-mode-lazy) (not font-lock-support-mode)))
     ;; No support mode set and none required - leave it alone
     ((or (not font-lock-support-mode) ;; No support mode set (but required)
	  (symbolp font-lock-support-mode)) ;; or a fixed mode for all
      (setq font-lock-support-mode
	    (list (cons 'rst-mode (and rst-mode-lazy 'lazy-lock-mode))
		  (cons t font-lock-support-mode))))
     ((and (listp font-lock-support-mode)
	   (not (assoc 'rst-mode font-lock-support-mode)))
      ;; A list of modes missing rst-mode
      (setq font-lock-support-mode
	    (append '((cons 'rst-mode (and rst-mode-lazy 'lazy-lock-mode)))
		    font-lock-support-mode)))))

  ;; Names and hooks
  (setq mode-name "reST")
  (setq major-mode 'rst-mode)
  (run-hooks 'text-mode-hook)
  (run-hooks 'rst-mode-hook))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Font lock

(defun rst-font-lock-keywords-function ()
  "Returns keywords to highlight in rst mode according to current settings."
  ;; The reST-links in the comments below all relate to sections in
  ;; http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
  (let* ( ;; This gets big - so let's define some abbreviations
	 ;; horizontal white space
	 (re-hws "[\t ]")
	 ;; beginning of line with possible indentation
	 (re-bol (concat "^" re-hws "*"))
	 ;; Separates block lead-ins from their content
	 (re-blksep1 (concat "\\(" re-hws "+\\|$\\)"))
	 ;; explicit markup tag
	 (re-emt "\\.\\.")
	 ;; explicit markup start
	 (re-ems (concat re-emt re-hws "+"))
	 ;; inline markup prefix
	 (re-imp1 (concat "\\(^\\|" re-hws "\\|[-'\"([{</:]\\)"))
	 ;; inline markup suffix
	 (re-ims1 (concat "\\(" re-hws "\\|[]-'\")}>/:.,;!?\\]\\|$\\)"))
	 ;; symbol character
	 (re-sym1 "\\(\\sw\\|\\s_\\)")
	 ;; inline markup content begin
	 (re-imbeg2 "\\(\\S \\|\\S \\([^")

	 ;; There seems to be a bug leading to error "Stack overflow in regexp
	 ;; matcher" when "|" or "\\*" are the characters searched for
	 (re-imendbeg
	  (if (< emacs-major-version 21)
	      "]"
	    "\\]\\|\\\\."))
	 ;; inline markup content end
	 (re-imend (concat re-imendbeg "\\)*[^\t \\\\]\\)"))
	 ;; inline markup content without asterisk
	 (re-ima2 (concat re-imbeg2 "*" re-imend))
	 ;; inline markup content without backquote
	 (re-imb2 (concat re-imbeg2 "`" re-imend))
	 ;; inline markup content without vertical bar
	 (re-imv2 (concat re-imbeg2 "|" re-imend))
	 ;; Supported URI schemes
	 (re-uris1 "\\(acap\\|cid\\|data\\|dav\\|fax\\|file\\|ftp\\|gopher\\|http\\|https\\|imap\\|ldap\\|mailto\\|mid\\|modem\\|news\\|nfs\\|nntp\\|pop\\|prospero\\|rtsp\\|service\\|sip\\|tel\\|telnet\\|tip\\|urn\\|vemmi\\|wais\\)")
	 ;; Line starting with adornment and optional whitespace; complete
	 ;; adornment is in (match-string 1); there must be at least 3
	 ;; characters because otherwise explicit markup start would be
	 ;; recognized
	 (re-ado2 (concat "^\\(\\(["
			  (if (or
			       (< emacs-major-version 21)
			       (save-match-data
				 (string-match "XEmacs\\|Lucid" emacs-version)))
			      "^a-zA-Z0-9 \t\x00-\x1F"
			    "^[:word:][:space:][:cntrl:]")
			  "]\\)\\2\\2+\\)" re-hws "*$"))
	 )
    (list
     ;; FIXME: Block markup is not recognized in blocks after explicit markup
     ;; start

     ;; Simple `Body Elements`_
     ;; `Bullet Lists`_
     (list
      (concat re-bol "\\([-*+]" re-blksep1 "\\)")
      1 rst-block-face)
     ;; `Enumerated Lists`_
     (list
      (concat re-bol "\\((?\\([0-9]+\\|[A-Za-z]\\|[IVXLCMivxlcm]+\\)[.)]"
	      re-blksep1 "\\)")
      1 rst-block-face)
     ;; `Definition Lists`_ FIXME: missing
     ;; `Field Lists`_
     (list
      (concat re-bol "\\(:[^:]+:\\)" re-blksep1)
      1 rst-external-face)
     ;; `Option Lists`_
     (list
      (concat re-bol "\\(\\(\\(\\([-+/]\\|--\\)\\sw\\(-\\|\\sw\\)*"
	      "\\([ =]\\S +\\)?\\)\\(,[\t ]\\)?\\)+\\)\\($\\|[\t ]\\{2\\}\\)")
      1 rst-block-face)

     ;; `Tables`_ FIXME: missing

     ;; All the `Explicit Markup Blocks`_
     ;; `Footnotes`_ / `Citations`_
     (list
      (concat re-bol "\\(" re-ems "\\[[^[]+\\]\\)" re-blksep1)
      1 rst-definition-face)
     ;; `Directives`_ / `Substitution Definitions`_
     (list
      (concat re-bol "\\(" re-ems "\\)\\(\\(|[^|]+|[\t ]+\\)?\\)\\("
	      re-sym1 "+::\\)" re-blksep1)
      (list 1 rst-directive-face)
      (list 2 rst-definition-face)
      (list 4 rst-directive-face))
     ;; `Hyperlink Targets`_
     (list
      (concat re-bol "\\(" re-ems "_\\([^:\\`]\\|\\\\.\\|`[^`]+`\\)+:\\)"
	      re-blksep1)
      1 rst-definition-face)
     (list
      (concat re-bol "\\(__\\)" re-blksep1)
      1 rst-definition-face)

     ;; All `Inline Markup`_
     ;; FIXME: Condition 5 preventing fontification of e.g. "*" not implemented
     ;; `Strong Emphasis`_
     (list
      (concat re-imp1 "\\(\\*\\*" re-ima2 "\\*\\*\\)" re-ims1)
      2 rst-emphasis2-face)
     ;; `Emphasis`_
     (list
      (concat re-imp1 "\\(\\*" re-ima2 "\\*\\)" re-ims1)
      2 rst-emphasis1-face)
     ;; `Inline Literals`_
     (list
      (concat re-imp1 "\\(``" re-imb2 "``\\)" re-ims1)
      2 rst-literal-face)
     ;; `Inline Internal Targets`_
     (list
      (concat re-imp1 "\\(_`" re-imb2 "`\\)" re-ims1)
      2 rst-definition-face)
     ;; `Hyperlink References`_
     ;; FIXME: `Embedded URIs`_ not considered
     (list
      (concat re-imp1 "\\(\\(`" re-imb2 "`\\|\\sw+\\)__?\\)" re-ims1)
      2 rst-reference-face)
     ;; `Interpreted Text`_
     (list
      (concat re-imp1 "\\(\\(:" re-sym1 "+:\\)?\\)\\(`" re-imb2 "`\\)\\(\\(:"
	      re-sym1 "+:\\)?\\)" re-ims1)
      (list 2 rst-directive-face)
      (list 5 rst-external-face)
      (list 8 rst-directive-face))
     ;; `Footnote References`_ / `Citation References`_
     (list
      (concat re-imp1 "\\(\\[[^]]+\\]_\\)" re-ims1)
      2 rst-reference-face)
     ;; `Substitution References`_
     (list
      (concat re-imp1 "\\(|" re-imv2 "|\\)" re-ims1)
      2 rst-reference-face)
     ;; `Standalone Hyperlinks`_
     (list
      ;; FIXME: This takes it easy by using a whitespace as delimiter
      (concat re-imp1 "\\(" re-uris1 ":\\S +\\)" re-ims1)
      2 rst-definition-face)
     (list
      (concat re-imp1 "\\(" re-sym1 "+@" re-sym1 "+\\)" re-ims1)
      2 rst-definition-face)

     ;; Do all block fontification as late as possible so 'append works

     ;; Sections_ / Transitions_
     (append
      (list
       re-ado2)
      (if (not rst-mode-lazy)
	  (list 1 rst-block-face)
	(list
	 (list 'rst-font-lock-handle-adornment
	       '(progn
		  (setq rst-font-lock-adornment-point (match-end 1))
		  (point-max))
	       nil
	       (list 1 '(cdr (assoc nil rst-adornment-faces-alist))
		     'append t)
	       (list 2 '(cdr (assoc rst-font-lock-level
				    rst-adornment-faces-alist))
		     'append t)
	       (list 3 '(cdr (assoc nil rst-adornment-faces-alist))
		     'append t)))))

     ;; `Comments`_
     (append
      (list
       (concat re-bol "\\(" re-ems "\\)\[^[|_]\\([^:]\\|:\\([^:]\\|$\\)\\)*$")
       (list 1 rst-comment-face))
      (if rst-mode-lazy
	  (list
	   (list 'rst-font-lock-find-unindented-line
		 '(progn
		    (setq rst-font-lock-indentation-point (match-end 1))
		    (point-max))
		 nil
		 (list 0 rst-comment-face 'append)))))
     (append
      (list
       (concat re-bol "\\(" re-emt "\\)\\(\\s *\\)\\?$")
       (list 1 rst-comment-face)
       (list 2 rst-comment-face))
      (if rst-mode-lazy
	  (list
	   (list 'rst-font-lock-find-unindented-line
		 '(progn
		    (setq rst-font-lock-indentation-point 'next)
		    (point-max))
		 nil
		 (list 0 rst-comment-face 'append)))))

     ;; `Literal Blocks`_
     (append
      (list
       (concat re-bol "\\(\\([^.\n]\\|\\.[^.\n]\\).*\\)?\\(::\\)$")
       (list 3 rst-block-face))
      (if rst-mode-lazy
	  (list
	   (list 'rst-font-lock-find-unindented-line
		 '(progn
		    (setq rst-font-lock-indentation-point t)
		    (point-max))
		 nil
		 (list 0 rst-literal-face 'append)))))
     )))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Indented blocks

(defun rst-forward-indented-block (&optional column limit)
  "Move forward across one indented block.
Find the next non-empty line which is not indented at least to COLUMN (defaults
to the column of the point). Moves point to first character of this line or the
first empty line immediately before it and returns that position. If there is
no such line before LIMIT (defaults to the end of the buffer) returns nil and
point is not moved."
  (interactive)
  (let ((clm (or column (current-column)))
	(start (point))
	fnd beg cand)
    (if (not limit)
	(setq limit (point-max)))
    (save-match-data
      (while (and (not fnd) (< (point) limit))
	(forward-line 1)
	(when (< (point) limit)
	  (setq beg (point))
	  (if (looking-at "\\s *$")
	      (setq cand (or cand beg)) ; An empty line is a candidate
	    (move-to-column clm)
	    ;; FIXME: No indentation [(zerop clm)] must be handled in some
	    ;; useful way - though it is not clear what this should mean at all
	    (if (string-match
		 "^\\s *$" (buffer-substring-no-properties beg (point)))
		(setq cand nil) ; An indented line resets a candidate
	      (setq fnd (or cand beg)))))))
    (goto-char (or fnd start))
    fnd))

;; Stores the point where the current indentation ends if a number. If `next'
;; indicates `rst-font-lock-find-unindented-line' shall take the indentation
;; from the next line if this is not empty. If non-nil indicates
;; `rst-font-lock-find-unindented-line' shall take the indentation from the
;; next non-empty line. Also used as a trigger for
;; `rst-font-lock-find-unindented-line'.
(defvar rst-font-lock-indentation-point nil)

(defun rst-font-lock-find-unindented-line (limit)
  (let* ((ind-pnt rst-font-lock-indentation-point)
	 (beg-pnt ind-pnt))
    ;; May run only once - enforce this
    (setq rst-font-lock-indentation-point nil)
    (when (and ind-pnt (not (numberp ind-pnt)))
      ;; Find indentation point in next line if any
      (setq ind-pnt
	    (save-excursion
	      (save-match-data
		(if (eq ind-pnt 'next)
		    (when (and (zerop (forward-line 1)) (< (point) limit))
		      (setq beg-pnt (point))
		      (when (not (looking-at "\\s *$"))
			(looking-at "\\s *")
			(match-end 0)))
		  (while (and (zerop (forward-line 1)) (< (point) limit)
			      (looking-at "\\s *$")))
		  (when (< (point) limit)
		    (setq beg-pnt (point))
		    (looking-at "\\s *")
		    (match-end 0)))))))
    (when ind-pnt
      (goto-char ind-pnt)
      ;; Always succeeds because the limit set by PRE-MATCH-FORM is the
      ;; ultimate point to find
      (goto-char (or (rst-forward-indented-block nil limit) limit))
      (set-match-data (list beg-pnt (point)))
      t)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Adornments

;; Stores the point where the current adornment ends. Also used as a trigger
;; for `rst-font-lock-handle-adornment'.
(defvar rst-font-lock-adornment-point nil)

;; Here `rst-font-lock-handle-adornment' stores the section level of the
;; current adornment or t for a transition.
(defvar rst-font-lock-level nil)

;; FIXME: It would be good if this could be used to markup section titles of
;; given level with a special key; it would be even better to be able to
;; customize this so it can be used for a generally available personal style
;;
;; FIXME: There should be some way to reset and reload this variable - probably
;; a special key
;;
;; FIXME: Some support for `outline-mode' would be nice which should be based
;; on this information
(defvar rst-adornment-level-alist nil
  "Associates adornments with section levels.
The key is a two character string. The first character is the adornment
character. The second character distinguishes underline section titles (`u')
from overline/underline section titles (`o'). The value is the section level.

This is made buffer local on start and adornments found during font lock are
entered.")

;; Returns section level for adornment key KEY. Adds new section level if KEY
;; is not found and ADD. If KEY is not a string it is simply returned.
(defun rst-adornment-level (key &optional add)
  (let ((fnd (assoc key rst-adornment-level-alist))
	(new 1))
    (cond
     ((not (stringp key))
      key)
     (fnd
      (cdr fnd))
     (add
      (while (rassoc new rst-adornment-level-alist)
	(setq new (1+ new)))
      (setq rst-adornment-level-alist
	    (append rst-adornment-level-alist (list (cons key new))))
      new))))

;; Classifies adornment for section titles and transitions. ADORNMENT is the
;; complete adornment string as found in the buffer. END is the point after the
;; last character of ADORNMENT. For overline section adornment LIMIT limits the
;; search for the matching underline. Returns a list. The first entry is t for
;; a transition, or a key string for `rst-adornment-level' for a section title.
;; The following eight values forming four match groups as can be used for
;; `set-match-data'. First match group contains the maximum points of the whole
;; construct. Second and last match group matched pure section title adornment
;; while third match group matched the section title text or the transition.
;; Each group but the first may or may not exist.
(defun rst-classify-adornment (adornment end limit)
  (save-excursion
    (save-match-data
      (goto-char end)
      (let ((ado-ch (aref adornment 0))
	    (ado-re (regexp-quote adornment))
	    (end-pnt (point))
	    (beg-pnt (progn
		       (forward-line 0)
		       (point)))
	    (nxt-emp
	     (save-excursion
	       (or (not (zerop (forward-line 1)))
		   (looking-at "\\s *$"))))
	    (prv-emp
	     (save-excursion
	       (or (not (zerop (forward-line -1)))
		   (looking-at "\\s *$"))))
	    key beg-ovr end-ovr beg-txt end-txt beg-und end-und)
	(cond
	 ((and nxt-emp prv-emp)
	  ;; A transition
	  (setq key t)
	  (setq beg-txt beg-pnt)
	  (setq end-txt end-pnt))
	 (prv-emp
	  ;; An overline
	  (setq key (concat (list ado-ch) "o"))
	  (setq beg-ovr beg-pnt)
	  (setq end-ovr end-pnt)
	  (forward-line 1)
	  (setq beg-txt (point))
	  (while (and (< (point) limit) (not end-txt))
	    (if (looking-at "\\s *$")
		;; No underline found
		(setq end-txt (1- (point)))
	      (when (looking-at (concat "\\(" ado-re "\\)\\s *$"))
		(setq end-und (match-end 1))
		(setq beg-und (point))
		(setq end-txt (1- beg-und))))
	    (forward-line 1)))
	 (t
	  ;; An underline
	  (setq key (concat (list ado-ch) "u"))
	  (setq beg-und beg-pnt)
	  (setq end-und end-pnt)
	  (setq end-txt (1- beg-und))
	  (setq beg-txt (progn
			  (if (re-search-backward "^\\s *$" 1 'move)
			      (forward-line 1))
			  (point)))))
	(list key
	      (or beg-ovr beg-txt beg-und)
	      (or end-und end-txt end-und)
	      beg-ovr end-ovr beg-txt end-txt beg-und end-und)))))

;; Handles adornments for font-locking section titles and transitions. Returns
;; three match groups. First and last match group matched pure overline /
;; underline adornment while second group matched section title text. Each
;; group may not exist.
(defun rst-font-lock-handle-adornment (limit)
  (let ((ado-pnt rst-font-lock-adornment-point))
    ;; May run only once - enforce this
    (setq rst-font-lock-adornment-point nil)
    (if ado-pnt
      (let* ((ado (rst-classify-adornment (match-string-no-properties 1)
					  ado-pnt limit))
	     (key (car ado))
	     (mtc (cdr ado)))
	(setq rst-font-lock-level (rst-adornment-level key t))
	(goto-char (nth 1 mtc))
	(set-match-data mtc)
	t))))

;;; rst-mode.el ends here



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Support for conversion from within Emacs

(defgroup rst-compile nil
  "Settings for support of conversion of reStructuredText
document with \\[rst-compile]."
  :group 'rst
  :version "21.1")

(defvar rst-compile-toolsets
  '((html . ("rst2html.py" ".html" nil))
    (latex . ("rst2latex.py" ".tex" nil))
    (newlatex . ("rst2newlatex.py" ".tex" nil))
    (pseudoxml . ("rst2pseudoxml.py" ".xml" nil))
    (xml . ("rst2xml.py" ".xml" nil)))
  "An association list of the toolset to a list of the (command to use,
extension of produced filename, options to the tool (nil or a
string)) to be used for converting the document.")

;; Note for Python programmers not familiar with association lists: you can set
;; values in an alists like this, e.g. :
;; (setcdr (assq 'html rst-compile-toolsets)
;;      '("rst2html.py" ".htm" "--stylesheet=/docutils.css"))


(defvar rst-compile-primary-toolset 'html
  "The default toolset for rst-compile.")

(defvar rst-compile-secondary-toolset 'latex
  "The default toolset for rst-compile with a prefix argument.")

(defun rst-compile-find-conf ()
  "Look for the configuration file in the parents of the current path."
  (interactive)
  (let ((file-name "docutils.conf")
        (buffer-file (buffer-file-name)))
    ;; Move up in the dir hierarchy till we find a change log file.
    (let ((dir (file-name-directory buffer-file)))
      (while (and (or (not (string= "/" dir)) (setq dir nil) nil)
                  (not (file-exists-p (concat dir file-name))))
        ;; Move up to the parent dir and try again.
        (setq dir (expand-file-name (file-name-directory
                                     (directory-file-name
                                     (file-name-directory dir))))) )
      (or (and dir (concat dir file-name)) nil)
    )))

(defun rst-compile (&optional pfxarg)
  "Compile command to convert reST document into some output file.
Attempts to find configuration file, if it can, overrides the
options."
  (interactive "P")
  ;; Note: maybe we want to check if there is a Makefile too and not do anything
  ;; if that is the case.  I dunno.
  (let* ((toolset (cdr (assq (if pfxarg
				 rst-compile-secondary-toolset
			       rst-compile-primary-toolset)
			rst-compile-toolsets)))
         (command (car toolset))
         (extension (cadr toolset))
         (options (caddr toolset))
         (conffile (rst-compile-find-conf))
         (bufname (file-name-nondirectory buffer-file-name))
         (outname (file-name-sans-extension bufname)))

    ;; Set compile-command before invocation of compile.
    (set (make-local-variable 'compile-command)
         (mapconcat 'identity
                    (list command
                          (or options "")
                          (if conffile
                              (concat "--config=\"" conffile "\"")
                            "")
                          bufname
                          (concat outname extension))
                    " "))

    ;; Invoke the compile command.
    (if (or compilation-read-command current-prefix-arg)
        (call-interactively 'compile)
      (compile compile-command))
    ))



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Generic text functions that are more convenient than the defaults.
;;

(defun replace-lines (fromchar tochar)
  "Replace flush-left lines, consisting of multiple FROMCHAR characters,
with equal-length lines of TOCHAR."
  (interactive "\
cSearch for flush-left lines of char:
cand replace with char: ")
  (save-excursion
    (let* ((fromstr (string fromchar))
           (searchre (concat "^" (regexp-quote fromstr) "+ *$"))
           (found 0))
      (condition-case err
          (while t
            (search-forward-regexp searchre)
            (setq found (1+ found))
            (search-backward fromstr)  ;; point will be *before* last char
            (setq p (1+ (point)))
            (beginning-of-line)
            (setq l (- p (point)))
            (rst-delete-line)
            (insert-char tochar l))
        (search-failed
         (message (format "%d lines replaced." found)))))))

(defun join-paragraph ()
  "Join lines in current paragraph into one line, removing end-of-lines."
  (interactive)
  (let ((fill-column 65000)) ; some big number
    (call-interactively 'fill-paragraph)))

;; FIXME: can we remove this?
(defun force-fill-paragraph ()
  "Fill paragraph at point, first joining the paragraph's lines into one.
This is useful for filling list item paragraphs."
  (interactive)
  (join-paragraph)
  (fill-paragraph nil))


;; Generic character repeater function.
;; For sections, better to use the specialized function above, but this can
;; be useful for creating separators.
(defun repeat-last-character (&optional tofill)
  "Fills the current line up to the length of the preceding line (if not
empty), using the last character on the current line.  If the preceding line is
empty, we use the fill-column.

If a prefix argument is provided, use the next line rather than the preceding
line.

If the current line is longer than the desired length, shave the characters off
the current line to fit the desired length.

As an added convenience, if the command is repeated immediately, the alternative
column is used (fill-column vs. end of previous/next line)."
  (interactive)
  (let* ((curcol (current-column))
         (curline (+ (count-lines (point-min) (point))
                     (if (eq curcol 0) 1 0)))
         (lbp (line-beginning-position 0))
         (prevcol (if (and (= curline 1) (not current-prefix-arg))
                      fill-column
                    (save-excursion
                      (forward-line (if current-prefix-arg 1 -1))
                      (end-of-line)
                      (skip-chars-backward " \t" lbp)
                      (let ((cc (current-column)))
                        (if (= cc 0) fill-column cc)))))
         (rightmost-column
          (cond (tofill fill-column)
                ((equal last-command 'repeat-last-character)
                 (if (= curcol fill-column) prevcol fill-column))
                (t (save-excursion
                     (if (= prevcol 0) fill-column prevcol)))
                )) )
    (end-of-line)
    (if (> (current-column) rightmost-column)
        ;; shave characters off the end
        (delete-region (- (point)
                          (- (current-column) rightmost-column))
                       (point))
      ;; fill with last characters
      (insert-char (preceding-char)
                   (- rightmost-column (current-column))))
    ))



(provide 'rst)
;;; rst.el ends here
