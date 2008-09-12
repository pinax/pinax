# core.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import re

import genshi.builder as bldr

__docformat__ = 'restructuredtext en'

escape_char = '~'
esc_neg_look = '(?<!' + re.escape(escape_char) + ')'
esc_to_remove = re.compile(''.join([r'(?<!',re.escape(escape_char),')',re.escape(escape_char),r'(?!([ \n]|$))']))
place_holder_re = re.compile(r'<<<(-?\d+?)>>>')
max_blank_lines = 250

def fill_from_store(text,element_store):
    frags = []
    mo = place_holder_re.search(text)
    while mo:
        if mo.start():
            frags.append(text[:mo.start()])
        frags.append(element_store.get(mo.group(1),
                       mo.group(1).join(['<<<','>>>'])))
        if mo.end() < len(text):
            text = text[mo.end():]
        else:
            break
        mo = place_holder_re.search(text)
    else:
        frags.append(text)
    return frags


def fragmentize(text,wiki_elements, element_store,remove_escapes=True):

    """Takes a string of wiki markup and outputs a list of genshi
    Fragments (Elements and strings).

    This recursive function, with help from the WikiElement objects,
    does almost all the parsing.

    When no WikiElement objects are supplied, escapes are removed from
    ``text`` (except if remove_escapes=True)  and it is
    returned as-is. This is the only way for recursion to stop.

    :parameters:
      text
        the text to be parsed
      wiki_elements
        list of WikiElement objects to be searched for
      remove_escapes
        If False, escapes will not be removed
    
    """

    while wiki_elements:
        # If the first supplied wiki_element is actually a list of elements, \
        # search for all of them and match the closest one only.
        if isinstance(wiki_elements[0],(list,tuple)):
            x = None
            mo = None
            for element in wiki_elements[0]:
                m = element.regexp.search(text)
                if m:
                    if x is None:
                        x,wiki_element,mo = m.start(),element,m
                    elif m.start() < x:
                        x,wiki_element,mo = m.start(),element,m
        else:
            wiki_element = wiki_elements[0]
            mo = wiki_element.regexp.search(text)
             
        if mo:
            frags = wiki_element._process(mo, text, wiki_elements, element_store)
            break
        else:
            wiki_elements = wiki_elements[1:]

    # remove escape characters 
    else: 
        if remove_escapes:
            text = esc_to_remove.sub('',text)
        frags = fill_from_store(text,element_store)

    return frags


class Parser(object):

    """Instantiates a parser with specified behaviour"""
    
    def __init__(self,dialect, method='xhtml', strip_whitespace=False, encoding='utf-8'):
        """Constructor for Parser objects.

        :parameters:
          dialect
            A Creole instance
          method
            This value is passed to genshies Steam.render(). Possible values
            include ``xhtml``, ``html``, and ``xml``.
          strip_whitespace
            This value is passed Genshies Steam.render().
          encoding
            This value is passed Genshies Steam.render().
        """
        self.dialect = dialect
        self.method = method
        self.strip_whitespace = strip_whitespace
        self.encoding=encoding

    def generate(self,text,element_store=None,context='block'):
        """Returns a Genshi Stream.

        :parameters:
          text
            The text to be parsed.
          context
            This is useful for marco development where (for example) supression
            of paragraph tags is desired. Can be 'inline', 'block', or a list
            of WikiElement objects (use with caution).
          element_store
            Internal dictionary that's passed around a lot ;)
            
        See Genshi documentation for additional keyword arguments.
          
        """
        if element_store is None:
            element_store = {}
        if not isinstance(context,list):
            if context == 'block':
                top_level_elements = self.dialect.block_elements
                do_preprocess = True
            elif context == 'inline':
                top_level_elements = self.dialect.inline_elements
                do_preprocess = False
        else:
            top_level_elements = context
            do_preprocess = False

        if do_preprocess:
            chunks = preprocess(text,self.dialect)
        else:
            chunks = [text]

        return bldr.tag(*[fragmentize(text,top_level_elements,element_store) for text in chunks]).generate()

    def render(self,text,element_store=None,context='block',**kwargs):
        """Returns final output string (e.g., xhtml)

        See generate() (above) and Genshi documentation for keyword arguments.
        """
        if element_store is None:
            element_store = {}
        return self.generate(text,element_store,context).render(method=self.method,strip_whitespace=self.strip_whitespace,
                                          encoding=self.encoding,**kwargs)

    def __call__(self,text,element_store=None,context='block'):
        """Wrapper for the render method. Returns final output string.

        See generate() (above) and Genshi documentation for keyword arguments.
        """

        if element_store is None:
            element_store = {}
        return self.render(text,element_store,context)


def preprocess(text, dialect):
    """This should generally be called before fragmentize().

    :parameters:
      text
        text to be processsed.
      dialect
        a ``Creole`` object.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = ''.join([text.rstrip(),'\n'])
    blank_lines = list(dialect.blank_line.regexp.finditer(text))
    if len(blank_lines) > max_blank_lines:
        return chunk(text,blank_lines,[dialect.pre,dialect.bodied_block_macro],max_blank_lines)

    return [text]


def chunk(text, blank_lines, hard_elements, limit):
    """Safely breaks large Creole documents into a list of smaller
    ones (strings)
    """
    hard_spans = []
    for e in hard_elements:
        for mo in e.regexp.finditer(text):
            hard_spans.append(mo.span())

    hard_chars = []
    for x,y in hard_spans:
        hard_chars.extend(range(x,y))
    hard_chars = set(hard_chars)

    chunks = []
    start = 0
    for i in range(len(blank_lines)/limit):
        for mo in blank_lines[limit/2 + i*limit:limit*3/2+i*limit:10]:
            if mo.start() not in hard_chars:
                chunks.append(text[start:mo.start()])
                start = mo.end()
                break
    chunks.append(text[start:])
    
    return chunks



def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

