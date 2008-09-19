# -*- coding: utf-8 -*-
"""
    pygments.formatters.img
    ~~~~~~~~~~~~~~~~~~~~~~~

    Formatter for Pixmap output.

    :copyright: 2007 by Ali Afshar.
    :license: BSD, see LICENSE for more details.
"""

import sys
from commands import getstatusoutput

from pygments.formatter import Formatter
from pygments.util import get_bool_opt, get_int_opt, get_choice_opt

# Import this carefully
try:
    import Image, ImageDraw, ImageFont
    pil_available = True
except ImportError:
    pil_available = False

try:
    import _winreg
except ImportError:
    _winreg = None

__all__ = ['ImageFormatter']


# For some unknown reason every font calls it something different
STYLES = {
    'NORMAL':     ['', 'Roman', 'Book', 'Normal', 'Regular', 'Medium'],
    'ITALIC':     ['Oblique', 'Italic'],
    'BOLD':       ['Bold'],
    'BOLDITALIC': ['Bold Oblique', 'Bold Italic'],
}

# A sane default for modern systems
DEFAULT_FONT_NAME_NIX = 'Bitstream Vera Sans Mono'
DEFAULT_FONT_NAME_WIN = 'Courier New'


class PilNotAvailable(ImportError):
    """When Python imaging library is not available"""


class FontNotFound(Exception):
    """When there are no usable fonts specified"""


class FontManager(object):
    """
    Manages a set of fonts: normal, italic, bold, etc...
    """

    def __init__(self, font_name, font_size=14):
        self.font_name = font_name
        self.font_size = font_size
        self.fonts = {}
        if sys.platform.startswith('win'):
            if not font_name:
                self.font_name = DEFAULT_FONT_NAME_WIN
            self._create_win()
        else:
            if not font_name:
                self.font_name = DEFAULT_FONT_NAME_NIX
            self._create_nix()

    def _get_nix_font_path(self, name, style):
        exit, out = getstatusoutput('fc-list "%s:style=%s" file' %
                                    (name, style))
        if not exit:
            lines = out.splitlines()
            if lines:
                path = lines[0].strip().strip(':')
                return path

    def _create_nix(self):
        for name in STYLES['NORMAL']:
            path = self._get_nix_font_path(self.font_name, name)
            if path is not None:
                self.fonts['NORMAL'] = ImageFont.truetype(path, self.font_size)
                break
        else:
            raise FontNotFound('No usable fonts named: "%s"' %
                               self.font_name)
        for style in ('ITALIC', 'BOLD', 'BOLDITALIC'):
            for stylename in STYLES[style]:
                path = self._get_nix_font_path(self.font_name, stylename)
                if path is not None:
                    self.fonts[style] = ImageFont.truetype(path, self.font_size)
                    break
            else:
                if style == 'BOLDITALIC':
                    self.fonts[style] = self.fonts['BOLD']
                else:
                    self.fonts[style] = self.fonts['NORMAL']

    def _lookup_win(self, key, basename, styles, fail=False):
        for suffix in ('', ' (TrueType)'):
            for style in styles:
                try:
                    valname = '%s%s%s' % (basename, style and ' '+style, suffix)
                    val, _ = _winreg.QueryValueEx(key, valname)
                    return val
                except EnvironmentError:
                    continue
        else:
            if fail:
                raise FontNotFound('Font %s (%s) not found in registry' %
                                   (basename, styles[0]))
            return None

    def _create_win(self):
        try:
            key = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE,
                r'Software\Microsoft\Windows NT\CurrentVersion\Fonts')
        except EnvironmentError:
            try:
                key = _winreg.OpenKey(
                    _winreg.HKEY_LOCAL_MACHINE,
                    r'Software\Microsoft\Windows\CurrentVersion\Fonts')
            except EnvironmentError:
                raise FontNotFound('Can\'t open Windows font registry key')
        try:
            path = self._lookup_win(key, self.font_name, STYLES['NORMAL'], True)
            self.fonts['NORMAL'] = ImageFont.truetype(path, self.font_size)
            for style in ('ITALIC', 'BOLD', 'BOLDITALIC'):
                path = self._lookup_win(key, self.font_name, STYLES[style])
                if path:
                    self.fonts[style] = ImageFont.truetype(path, self.font_size)
                else:
                    if style == 'BOLDITALIC':
                        self.fonts[style] = self.fonts['BOLD']
                    else:
                        self.fonts[style] = self.fonts['NORMAL']
        finally:
            _winreg.CloseKey(key)

    def get_char_size(self):
        """
        Get the character size.
        """
        return self.fonts['NORMAL'].getsize('M')

    def get_font(self, bold, oblique):
        """
        Get the font based on bold and italic flags.
        """
        if bold and oblique:
            return self.fonts['BOLDITALIC']
        elif bold:
            return self.fonts['BOLD']
        elif oblique:
            return self.fonts['ITALIC']
        else:
            return self.fonts['NORMAL']


class ImageFormatter(Formatter):
    """
    Create an image from source code. This uses the Python Imaging Library to
    generate a pixmap from the source code.

    *New in Pygments 0.10.*

    Additional options accepted:

    `image_format`
        An image format to output to that is recognised by PIL, these include:

        * "PNG" (default)
        * "JPEG"
        * "BMP"
        * "GIF"

    `line_pad`
        The extra spacing (in pixels) between each line of text.

        Default: 2

    `font_name`
        The font name to be used as the base font from which others, such as
        bold and italic fonts will be generated.  This really should be a
        monospace font to look sane.

        Default: "Bitstream Vera Sans Mono"

    `font_size`
        The font size in points to be used.

        Default: 14

    `image_pad`
        The padding, in pixels to be used at each edge of the resulting image.

        Default: 10

    `line_numbers`
        Whether line numbers should be shown: True/False

        Default: True

    `line_number_step`
        The step used when printing line numbers.

        Default: 1

    `line_number_bg`
        The background colour (in "#123456" format) of the line number bar, or
        None to use the style background color.

        Default: "#eed"

    `line_number_fg`
        The text color of the line numbers (in "#123456"-like format).

        Default: "#886"

    `line_number_chars`
        The number of columns of line numbers allowable in the line number
        margin.

        Default: 2

    `line_number_bold`
        Whether line numbers will be bold: True/False

        Default: False

    `line_number_italic`
        Whether line numbers will be italicized: True/False

        Default: False

    `line_number_separator`
        Whether a line will be drawn between the line number area and the
        source code area: True/False

        Default: True

    `line_number_pad`
        The horizontal padding (in pixels) between the line number margin, and
        the source code area.

        Default: 6
    """

    # Required by the pygments mapper
    name = 'img'
    aliases = ['img', 'IMG', 'png', 'jpg', 'gif', 'bmp']
    filenames = ['*.png', '*.jpg', '*.gif', '*.bmp']

    unicodeoutput = False

    def __init__(self, **options):
        """
        See the class docstring for explanation of options.
        """
        if not pil_available:
            raise PilNotAvailable(
                'Python Imaging Library is required for this formatter')
        Formatter.__init__(self, **options)
        # Read the style
        self.styles = dict(self.style)
        if self.style.background_color is None:
            self.background_color = '#fff'
        else:
            self.background_color = self.style.background_color
        # Image options
        self.image_format = get_choice_opt(options, 'image_format',
            ['PNG', 'JPEG', 'GIF', 'BMP'], 'PNG')
        self.image_pad = get_int_opt(options, 'image_pad', 10)
        self.line_pad = get_int_opt(options, 'line_pad', 2)
        # The fonts
        self.fonts = FontManager(options.get('font_name', ''))
        self.fontw, self.fonth = self.fonts.get_char_size()
        # Line number options
        self.line_number_fg = options.get('line_number_fg', '#886')
        self.line_number_bg = options.get('line_number_bg', '#eed')
        self.line_number_chars = get_int_opt(options,
                                        'line_number_chars', 2)
        self.line_number_bold = get_bool_opt(options,
                                        'line_number_bold', False)
        self.line_number_italic = get_bool_opt(options,
                                        'line_number_italic', False)
        self.line_number_pad = get_int_opt(options, 'line_number_pad', 6)
        self.line_numbers = get_bool_opt(options, 'line_numbers', True)
        self.line_number_separator = get_bool_opt(options,
                                        'line_number_separator', True)
        self.line_number_step = get_int_opt(options, 'line_number_step', 1)
        if self.line_numbers:
            self.line_number_width = (self.fontw * self.line_number_chars +
                                   self.line_number_pad * 2)
        else:
            self.line_number_width = 0
        self.drawables = []

    def _get_line_height(self):
        """
        Get the height of a line.
        """
        return self.fonth + self.line_pad

    def _get_line_y(self, lineno):
        """
        Get the Y coordinate of a line number.
        """
        return lineno * self._get_line_height() + self.image_pad

    def _get_char_width(self):
        """
        Get the width of a character.
        """
        return self.fontw

    def _get_char_x(self, charno):
        """
        Get the X coordinate of a character position.
        """
        return charno * self.fontw + self.image_pad + self.line_number_width

    def _get_text_pos(self, charno, lineno):
        """
        Get the actual position for a character and line position.
        """
        return self._get_char_x(charno), self._get_line_y(lineno)

    def _get_linenumber_pos(self, lineno):
        """
        Get the actual position for the start of a line number.
        """
        return (self.image_pad, self._get_line_y(lineno))

    def _get_text_color(self, style):
        """
        Get the correct color for the token from the style.
        """
        if style['color'] is not None:
            fill = '#' + style['color']
        else:
            fill = '#000'
        return fill

    def _get_style_font(self, style):
        """
        Get the correct font for the style.
        """
        return self.fonts.get_font(style['bold'], style['italic'])

    def _get_image_size(self, maxcharno, maxlineno):
        """
        Get the required image size.
        """
        return (self._get_char_x(maxcharno) + self.image_pad,
                self._get_line_y(maxlineno + 0) + self.image_pad)

    def _draw_linenumber(self, lineno):
        """
        Remember a line number drawable to paint later.
        """
        self._draw_text(
            self._get_linenumber_pos(lineno),
            str(lineno + 1).rjust(self.line_number_chars),
            font=self.fonts.get_font(self.line_number_bold,
                                     self.line_number_italic),
            fill=self.line_number_fg,
        )

    def _draw_text(self, pos, text, font, **kw):
        """
        Remember a single drawable tuple to paint later.
        """
        self.drawables.append((pos, text, font, kw))

    def _create_drawables(self, tokensource):
        """
        Create drawables for the token content.
        """
        lineno = charno = maxcharno = 0
        for ttype, value in tokensource:
            while ttype not in self.styles:
                ttype = ttype.parent
            style = self.styles[ttype]
            value = value.expandtabs(4)
            lines = value.splitlines()
            #print lines
            for i, line in enumerate(lines):
                if not line:
                    lineno += 1
                    charno = 0
                else:
                    # add a line for each extra line in the value
                    if i:
                        lineno += 1
                        charno = 0
                    self._draw_text(
                        self._get_text_pos(charno, lineno),
                        line,
                        font = self._get_style_font(style),
                        fill = self._get_text_color(style)
                    )
                    charno += len(value)
                    maxcharno = max(maxcharno, charno)
        self.maxcharno = maxcharno
        self.maxlineno = lineno

    def _draw_line_numbers(self):
        """
        Create drawables for the line numbers.
        """
        if not self.line_numbers:
            return
        for i in xrange(self.maxlineno):
            if ((i + 1) % self.line_number_step) == 0:
                self._draw_linenumber(i)

    def _paint_line_number_bg(self, im):
        """
        Paint the line number background on the image.
        """
        if not self.line_numbers:
            return
        if self.line_number_fg is None:
            return
        draw = ImageDraw.Draw(im)
        recth = im.size[-1]
        rectw = self.image_pad + self.line_number_width - self.line_number_pad
        draw.rectangle([(0, 0),
                        (rectw, recth)],
             fill=self.line_number_bg)
        draw.line([(rectw, 0), (rectw, recth)], fill=self.line_number_fg)
        del draw

    def format(self, tokensource, outfile):
        """
        Format ``tokensource``, an iterable of ``(tokentype, tokenstring)``
        tuples and write it into ``outfile``.

        This implementation calculates where it should draw each token on the
        pixmap, then calculates the required pixmap size and draws the items.
        """
        self._create_drawables(tokensource)
        self._draw_line_numbers()
        im = Image.new(
            'RGB',
            self._get_image_size(self.maxcharno, self.maxlineno),
            self.background_color
        )
        self._paint_line_number_bg(im)
        draw = ImageDraw.Draw(im)
        for pos, value, font, kw in self.drawables:
            draw.text(pos, value, font=font, **kw)
        im.save(outfile, self.image_format)


