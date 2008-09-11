# -*- coding: utf-8 -*-
"""
    pygments.styles.vs
    ~~~~~~~~~~~~~~~~~~

    Simple style with MS Visual Studio colors.

    :copyright: 2008 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Whitespace


class VisualStudioStyle(Style):

    background_color = "#ffffff"
    default_style = ""

    styles = {
        Comment:                   "#008000",
        Comment.Preproc:           "#0000ff",
        Keyword:                   "#0000ff",
        Operator.Word:             "#0000ff",
        Keyword.Type:              "#2b91af",
        Name.Class:                "#2b91af",
        String:                    "#a31515",

        Generic.Heading:           "bold",
        Generic.Subheading:        "bold",
        Generic.Emph:              "italic",
        Generic.Strong:            "bold",
        Generic.Prompt:            "bold",

        Error:                     "border:#FF0000"
    }
