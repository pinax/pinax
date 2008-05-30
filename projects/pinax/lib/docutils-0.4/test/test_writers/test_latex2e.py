#! /usr/bin/env python

# Author: engelbert gruber
# Contact: grubert@users.sourceforge.net
# Revision: $Revision: 3840 $
# Date: $Date: 2005-08-27 15:43:58 +0200 (Sat, 27 Aug 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for latex2e writer.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.PublishTestSuite('latex')
    s.generateTests(totest)
    return s


latex_head = """\
\\documentclass[10pt,a4paper,english]{article}
\\usepackage{babel}
\\usepackage{ae}
\\usepackage{aeguill}
\\usepackage{shortvrb}
\\usepackage[latin1]{inputenc}
\\usepackage{tabularx}
\\usepackage{longtable}
\\setlength{\\extrarowheight}{2pt}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage{color}
\\usepackage{multirow}
\\usepackage{ifthen}
\\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\\usepackage[DIV12]{typearea}
%% generator Docutils: http://docutils.sourceforge.net/
\\newlength{\\admonitionwidth}
\\setlength{\\admonitionwidth}{0.9\\textwidth}
\\newlength{\\docinfowidth}
\\setlength{\\docinfowidth}{0.9\\textwidth}
\\newlength{\\locallinewidth}
\\newcommand{\\optionlistlabel}[1]{\\bf #1 \\hfill}
\\newenvironment{optionlist}[1]
{\\begin{list}{}
  {\\setlength{\\labelwidth}{#1}
   \\setlength{\\rightmargin}{1cm}
   \\setlength{\\leftmargin}{\\rightmargin}
   \\addtolength{\\leftmargin}{\\labelwidth}
   \\addtolength{\\leftmargin}{\\labelsep}
   \\renewcommand{\\makelabel}{\\optionlistlabel}}
}{\\end{list}}
\\newlength{\\lineblockindentation}
\\setlength{\\lineblockindentation}{2.5em}
\\newenvironment{lineblock}[1]
{\\begin{list}{}
  {\\setlength{\\partopsep}{\\parskip}
   \\addtolength{\\partopsep}{\\baselineskip}
   \\topsep0pt\\itemsep0.15\\baselineskip\\parsep0pt
   \\leftmargin#1}
 \\raggedright}
{\\end{list}}
% begin: floats for footnotes tweaking.
\\setlength{\\floatsep}{0.5em}
\\setlength{\\textfloatsep}{\\fill}
\\addtolength{\\textfloatsep}{3em}
\\renewcommand{\\textfraction}{0.5}
\\renewcommand{\\topfraction}{0.5}
\\renewcommand{\\bottomfraction}{0.5}
\\setcounter{totalnumber}{50}
\\setcounter{topnumber}{50}
\\setcounter{bottomnumber}{50}
% end floats for footnotes
% some commands, that could be overwritten in the style file.
\\newcommand{\\rubric}[1]{\\subsection*{~\\hfill {\\it #1} \\hfill ~}}
\\newcommand{\\titlereference}[1]{\\textsl{#1}}
% end of "some commands"
"""

totest = {}

totest['table_of_contents'] = [
# input
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
## # expected output
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}

\\setlength{\\locallinewidth}{\\linewidth}
\\hypertarget{table-of-contents}{}
\\pdfbookmark[0]{Table of Contents}{table-of-contents}
\\subsubsection*{~\\hfill Table of Contents\\hfill ~}
\\begin{list}{}{}
\\item {} \\href{\\#title-1}{Title 1}
\\begin{list}{}{}
\\item {} \\href{\#title-2}{Title 2}

\\end{list}

\\end{list}



%___________________________________________________________________________

\\hypertarget{title-1}{}
\\pdfbookmark[0]{Title 1}{title-1}
\\section*{Title 1}

Paragraph 1.


%___________________________________________________________________________

\\hypertarget{title-2}{}
\\pdfbookmark[1]{Title 2}{title-2}
\\subsection*{Title 2}

Paragraph 2.

\\end{document}
"""],

]


totest['enumerated_lists'] = [
# input
["""\
1. Item 1.
2. Second to the previous item this one will explain

  a) nothing.
  b) or some other.

3. Third is 

  (I) having pre and postfixes
  (II) in roman numerals.
""",
# expected output
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}

\\setlength{\\locallinewidth}{\\linewidth}
\\newcounter{listcnt1}
\\begin{list}{\\arabic{listcnt1}.}
{
\\usecounter{listcnt1}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item {} 
Item 1.

\\item {} 
Second to the previous item this one will explain

\\end{list}
\\begin{quote}
\\newcounter{listcnt2}
\\begin{list}{\\alph{listcnt2})}
{
\\usecounter{listcnt2}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item {} 
nothing.

\\item {} 
or some other.

\\end{list}
\\end{quote}
\\newcounter{listcnt3}
\\begin{list}{\\arabic{listcnt3}.}
{
\\usecounter{listcnt3}
\\addtocounter{listcnt3}{2}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item {} 
Third is

\\end{list}
\\begin{quote}
\\newcounter{listcnt4}
\\begin{list}{(\\Roman{listcnt4})}
{
\\usecounter{listcnt4}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item {} 
having pre and postfixes

\\item {} 
in roman numerals.

\\end{list}
\\end{quote}

\\end{document}
"""],
]

# BUG: need to test for quote replacing if language is de (ngerman).

totest['quote_mangling'] = [
# input
["""\
Depending on language quotes are converted for latex.
Expecting "en" here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test)::

    ""
    This is left "untouched" also *this*.
    ""

.. parsed-literal::

    should get "quotes" and *italics*.


Inline ``literal "quotes"`` should be kept.
""",
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}

\\setlength{\\locallinewidth}{\\linewidth}

Depending on language quotes are converted for latex.
Expecting ``en'' here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test):
\\begin{quote}{\\ttfamily \\raggedright \\noindent
"{}"~\\\\
This~is~left~"untouched"~also~*this*.~\\\\
"{}"
}\\end{quote}
\\begin{quote}{\\ttfamily \\raggedright \\noindent
should~get~"quotes"~and~\\emph{italics}.
}\\end{quote}

Inline \\texttt{literal "quotes"} should be kept.

\\end{document}
"""],
]

totest['table_caption'] = [
# input
["""\
.. table:: Foo

   +-----+-----+
   |     |     |
   +-----+-----+
   |     |     |
   +-----+-----+
""",
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}

\\setlength{\\locallinewidth}{\\linewidth}

\\begin{longtable}[c]{|p{0.07\locallinewidth}|p{0.07\locallinewidth}|}
\\caption{Foo}\\\\
\\hline
 &  \\\\
\hline
 &  \\\\
\hline
\\end{longtable}

\\end{document}
"""],
]

# In "\\\n[" the "[" needs to be protected (otherwise it will be seen as an option to "\\").
totest['brackett_protection'] = [
# input
["""\
::

  something before to get a end of line.
  [

  the empty line gets tested too
  ]
""",
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}

\\setlength{\\locallinewidth}{\\linewidth}
\\begin{quote}{\\ttfamily \\raggedright \\noindent
something~before~to~get~a~end~of~line.~\\\\
{[}~\\\\
~\\\\
the~empty~line~gets~tested~too~\\\\
{]}
}\\end{quote}

\\end{document}
"""],
]

totest['raw'] = [
["""\
.. raw:: latex

   \\noindent

A paragraph.

.. |sub| raw:: latex

   (some raw text)

Foo |sub|
same paragraph.
""",
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}

\\setlength{\\locallinewidth}{\\linewidth}
\\noindent
A paragraph.

Foo (some raw text)
same paragraph.

\\end{document}
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
