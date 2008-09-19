# elements.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import re
import urlparse

import genshi.builder as bldr
from genshi.core import Stream
from genshi.filters import HTMLSanitizer

from core import escape_char, esc_neg_look, fragmentize 

sanitizer = HTMLSanitizer()

__docformat__ = 'restructuredtext en'

class WikiElement(object):
    
    """Baseclass for all wiki elements."""
    
    append_newline = False
    """Determines if newlines are appended to Element(s) during processing.
    Should only affect readability of source xml.
    """
    
    def __init__(self, tag, token, child_tags):
        """Constructor for WikiElement objects.

        Subclasses may have other keyword arguments.   

        :parameters:
          tag
            The xhtml tag associated with the element.
          token
            The character string (or strings) that identifies the element
            in wiki markup.
          child_tags
            A list of wiki_elements that will be searched for in the body of the
            element.  The order of these elements matters, because if an element is
            found before the element that encloses it, the enclosing element will
            never be found.  In cases where this imposes limits (e.g, ``strong`` and
            ``em`` should be allowed to nest each other), place the conflicting
            elements in a sublist. The parser will then find which comes first.
        """
        self.tag = tag
        self.token = token
        self.child_tags = child_tags
                
    def _build(self,mo,element_store):
        """Returns a genshi Element that has ``self.tag`` as the
        outermost tag.

        This methods if called exclusively by ``_process``

        :parameters:
          mo
            match object, usually the one returned by
            self.regexp.search(s) 
        """
        return bldr.tag.__getattr__(self.tag)(fragmentize(mo.group(1),
                                                          self.child_tags,
                                                          element_store))

    def re_string(self):
        """The regular expression pattern that is compiled into ``self.regexp``.

        The regular expression must consume the entire wiki element,
        including the tokens. For block elements, the newline on the last
        line must be consumed also. group(1) should normally be the
        entire string inside the tokens. If not, a custom ``_build``
        method will be needed.
        """
        pass

    def _process(self, mo, text, wiki_elements,element_store):
        """Returns genshi Fragments (Elements and text)

        This is mainly for block level markup. See InlineElement
        for the other method.
        """
        frags = []
        # call again for leading text and extend the result list 
        if mo.start():
            frags.extend(fragmentize(text[:mo.start()],wiki_elements[1:],
                                     element_store))
        # append the found wiki element to the result list
        frags.append(self._build(mo,element_store))
        # make the source output easier to read
        if self.append_newline:
            frags.append('\n')
        # call again for trailing text and extend the result list
        if mo.end() < len(text):
            frags.extend(fragmentize(text[mo.end():],wiki_elements,
                                     element_store))
        return frags
        
    def __repr__(self):
        return "<WikiElement "+str(self.tag)+">"

class InlineElement(WikiElement):

    r"""For finding generic inline elements like ``strong`` and ``em``.

    >>> em = InlineElement('em','//',[])
    >>> mo1 = em.regexp.search('a //word// in a line')
    >>> mo2 = em.regexp.search('a //word in a line\n or two\n')
    >>> mo1.group(0),mo1.group(1)
    ('//word//', 'word')
    >>> mo2.group(0),mo2.group(1)
    ('//word in a line\n or two', 'word in a line\n or two')

    Use a list for the ``token`` argument to have different start
    and end strings. These must be closed.

    >>> foo = InlineElement('foo',['<<','>>'],[])
    >>> mo = foo.regexp.search('blaa <<here it is >>\n')
    >>> mo.group(1)
    'here it is '
        
    """

    def __init__(self, tag, token, child_tags=[]):
        super(InlineElement,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL)

    def re_string(self):
        if isinstance(self.token,str):
            content = '(.+?)'
            end = '(' + esc_neg_look + re.escape(self.token) + r'|$)'
            return esc_neg_look + re.escape(self.token) + content + end
        else:
            content = '(.+?)'
            return esc_neg_look + re.escape(self.token[0]) + content + esc_neg_look + re.escape(self.token[1])

    def _process(self, mo, text, wiki_elements, element_store):
        """Returns genshi Fragments (Elements and text)"""
        processed = self._build(mo,element_store)
        store_id = str(id(processed)) 
        element_store[store_id] = processed
        text = ''.join([text[:mo.start()],'<<<',store_id,'>>>',
                        text[mo.end():]])
        frags = fragmentize(text,wiki_elements,element_store)
        return frags


macro_name = r'([a-zA-Z]+([-.]?[a-zA-Z0-9]+)*)'
"""allows any number of non-repeating hyphens or periods.
Underscore is not included because hyphen is"""

class Macro(WikiElement):
    r"""Finds and processes inline macro elements."""

    def __init__(self, tag, token, child_tags,func):
        super(Macro,self).__init__(tag,token , child_tags)
        self.func = func
        self.regexp = re.compile(self.re_string())


    def _process(self, mo, text, wiki_elements,element_store):
        """Returns genshi Fragments (Elements and text)"""
        processed = self._build(mo,element_store)
        if isinstance(processed, basestring):
            text = ''.join([text[:mo.start()],processed,
                        text[mo.end():]])
        else:
            store_id = str(id(processed))
            element_store[store_id] = processed
            text = ''.join([text[:mo.start()],'<<<',store_id,'>>>',
                        text[mo.end():]])
        frags = fragmentize(text,wiki_elements,element_store)
        return frags


    def re_string(self):
        content = '(.*?)'
        return esc_neg_look + re.escape(self.token[0]) + r'(' + macro_name + \
               content + ')' + esc_neg_look + re.escape(self.token[1])

    def _build(self,mo,element_store):
        if self.func:
            value = self.func(mo.group(2),mo.group(4),None,False)
        else:
            value = None
        if value is None:
            return bldr.tag(self.token[0] + mo.group(1) + self.token[1])
        elif isinstance(value,basestring):
            return value
        elif isinstance(value, (bldr.Element, Stream)):
            return [value]
        else:
            raise "Marcos can only return strings and Genshi Streams" 
        

class BodiedMacro(Macro):
    """Finds and processes macros with bodies.

    Does not span across top level block markup
    (see BodiedBlockMacro's for that)."""

    def __init__(self, tag, token, child_tags,func):
        super(BodiedMacro,self).__init__(tag,token , child_tags,func)
        self.func = func
        self.regexp = re.compile(self.re_string(),re.DOTALL)

    def re_string(self):
        content = r'([ \S]*?)'
        #macro_name = r'([a-zA-Z]+([-.]?[a-zA-Z0-9]+)*)'
        body = '(.+?)'
        return esc_neg_look + re.escape(self.token[0]) + r'(' + macro_name + \
               content + ')'+ esc_neg_look + re.escape(self.token[1]) + \
               body + esc_neg_look + re.escape(self.token[0]) + \
               r'/\2' + re.escape(self.token[1])

    def _build(self,mo,element_store):
        if self.func:
            value = self.func(mo.group(2),mo.group(4),mo.group(5),False)
        else:
            value = None
        if value is None:
            return bldr.tag(self.token[0] + mo.group(1) + self.token[1]
                            + mo.group(5) + self.token[0] + '/'
                            + mo.group(1) + self.token[1])
        elif isinstance(value, basestring):
            return value
        elif isinstance(value, (bldr.Element, Stream)):
            return [value]
        else:
            raise "macros can only return strings and genshi Streams"

class BlockMacro(WikiElement):
    """Finds a block macros.

    Macro must be on a line alone without leading spaces. Resulting
    output with not be enclosed in paragraph marks or consumed by
    other markup (except pre blocks and BodiedBlockMacro's)
    """

    def __init__(self, tag, token, child_tags,func):
        super(BlockMacro,self).__init__(tag,token , child_tags)
        self.func = func
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def _process(self, mo, text, wiki_elements,element_store):
        """Returns genshi Fragments (Elements and text)

        This is mainly for block level markup. See InlineElement
        for the other method.
        """

        processed = self._build(mo,element_store)
        if isinstance(processed, basestring):
            #print '_process', repr(processed)
            text = ''.join([text[:mo.start()],processed,
                        text[mo.end():]])
            frags = fragmentize(text,wiki_elements,element_store)
        else:
        
            frags = []
            # call again for leading text and extend the result list 
            if mo.start():
                frags.extend(fragmentize(text[:mo.start()],wiki_elements[1:],
                                         element_store))
            # append the found wiki element to the result list
            frags.append(processed)
            # make the source output easier to read
            if self.append_newline:
                frags.append('\n')
            # call again for trailing text and extend the result list
            if mo.end() < len(text):
                frags.extend(fragmentize(text[mo.end():],wiki_elements,
                                         element_store))
        return frags


    def re_string(self):
        arg_string = '((?!.*>>.*>>).*?)'

        
        #macro_name = r'([a-zA-Z]+([-.]?[a-zA-Z0-9]+)*)'
        # allows any number of non-repeating hyphens or periods
        # underscore is not included because hyphen is
        start = r'(^\s*?\n|\A)' + re.escape(self.token[0])
        end = re.escape(self.token[1]) + r'\s*?\n(\s*?\n|$)'
                
        return start + '(' + macro_name + arg_string + ')' + end


    def _build(self,mo,element_store):
        #print 'block_macro', mo.groups()
        if self.func:
            value = self.func(mo.group(3),mo.group(5),None,True)
        else:
            value = None
        if value is None:
            return bldr.tag(self.token[0] + mo.group(2) + self.token[1])
        elif isinstance(value,basestring):
            return ''.join([value.rstrip(),'\n'])
        elif isinstance(value, (bldr.Element, Stream)):
            return [value]
        else:
            raise "Marcos can only return strings and Genshi Streams" 
        

class BodiedBlockMacro(BlockMacro):
    """Finds and processes block macros with bodies.

    The opening and closing tokens must be are each on a line alone without
    leading spaces. These macros can enclose other block level markup
    including pre blocks and other BodiedBlockMacro's."""

    def __init__(self, tag, token, child_tags,func):
        super(BodiedBlockMacro,self).__init__(tag,token , child_tags,func)
        self.func = func
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        arg_string = r'((?![^\n]*>>[^\n]*>>)[ \S]*?)'
        start = '^' + re.escape(self.token[0])
        #macro_name = r'([a-zA-Z]+([-.]?[a-zA-Z0-9]+)*)'
        body = r'(.*?\n)'
        end = re.escape(self.token[0]) + \
               r'/\2' + re.escape(self.token[1]) + r'\s*?\n'
        
        return start + '(' + macro_name + arg_string + ')' + re.escape(self.token[1]) + \
               r'\s*?\n' + body + end

    def _build(self,mo,element_store):
        #print 'block_bodied_macro', mo.groups()
        if self.func:
            value = self.func(mo.group(2),mo.group(4),mo.group(5),True)
        else:
            value = None
        if value is None:
            return bldr.tag(self.token[0] + mo.group(1) + self.token[1]
                            + mo.group(5) + self.token[0] + '/'
                            + mo.group(1) + self.token[1])
        elif isinstance(value, basestring):
            return value
        elif isinstance(value, (bldr.Element, Stream)):
            return [value]
        else:
            raise "macros can only return strings and genshi Streams"
        
    
class RawLink(InlineElement):
    
    """Used to find raw urls in wiki text and build xml from them.

    >>> raw_link = RawLink(tag='a')
    >>> mo = raw_link.regexp.search(" a http://www.google.com url ")
    >>> raw_link.href(mo)
    'http://www.google.com'
    >>> raw_link._build(mo,{}).generate().render()
    '<a href="http://www.google.com">http://www.google.com</a>'
    
    """
    linking_protocols = ['http','https']
    
    def __init__(self, tag):
        super(RawLink,self).__init__(tag=tag, token=None, child_tags=None)
        self.regexp = re.compile(self.re_string())

    def re_string(self):
        escape = '(' + re.escape(escape_char) + ')?'
        protocol = '((https?|ftp)://'
        rest_of_url = r'\S+?)'
        #allow one punctuation character or '**' or '//'
        look_ahead = r'(?=([,.?!:;"\']|\*\*|//)?(\s|$))' 
        return escape + protocol + rest_of_url + look_ahead

    def _build(self,mo,element_store):
        if (not mo.group(1)) and (mo.group(3) in self.linking_protocols):
            return bldr.tag.__getattr__(self.tag)(self.alias(mo,element_store),
                                              href=self.href(mo))
        else:
            return self.href(mo)
        
    def href(self,mo):
        """Returns the string for the href attribute of the Element."""
        if sanitizer.is_safe_uri(mo.group(2)):
            return mo.group(2)
        else:
            return "unsafe_uri_detected"

    def alias(self,mo,element_store):
        """Returns the string for the content of the Element."""
        return self.href(mo)


class URLLink(WikiElement):
    
    """Used to find url type links inside a link.

    The scope of these is within link markup only (i.e., [[url]]

    >>> url_link = URLLink('a','',[],'|')
    >>> mo = url_link.regexp.search(" http://www.google.com| here ")
    >>> url_link.href(mo)
    'http://www.google.com'
    >>> url_link._build(mo,{}).generate().render()
    '<a href="http://www.google.com">here</a>'
    
    """

    def __init__(self, tag,token,child_tags,delimiter):
        super(URLLink,self).__init__(tag, token, child_tags)
        self.delimiter = delimiter
        self.regexp = re.compile(self.re_string())

    def re_string(self):
        protocol = r'^\s*((\w+?://|/)'
        rest_of_url = r'\S*?)\s*'
        alias = r'(' + re.escape(self.delimiter) + r' *(.*?))? *$'
        return protocol + rest_of_url + alias

    def _build(self,mo,element_store):
        return bldr.tag.__getattr__(self.tag)(self.alias(mo,element_store),
                                              href=self.href(mo))
       
    def href(self,mo):
        """Returns the string for the href attribute of the Element."""
        if sanitizer.is_safe_uri(mo.group(1)):
            return mo.group(1)
        else:
            return "unsafe_uri_detected"
            

    def alias(self,mo,element_store):
        """Returns the string for the content of the Element."""
        if not mo.group(4):
            return self.href(mo)
        else:
            return fragmentize(mo.group(4),self.child_tags,element_store)



class InterWikiLink(WikiElement):

    """Used to match interwiki links inside a link.

    The search scope for these is only inside links. 

    >>> interwiki_link = InterWikiLink('a','',[],
    ... delimiter1=':', delimiter2 = '|',
    ... base_urls=dict(somewiki='http://somewiki.org/',
    ...                bigwiki='http://bigwiki.net/'),
    ...                links_funcs={},default_space_char='_',
    ...                space_chars={})
    >>> mo = interwiki_link.regexp.search(" somewiki:Home Page|steve ")
    >>> interwiki_link.href(mo)
    'http://somewiki.org/Home_Page'
    >>> interwiki_link.alias(mo,{})
    ['steve']
    
    """

    def __init__(self, tag, token, child_tags,delimiter1,
                 delimiter2,base_urls,links_funcs,default_space_char,space_chars):
        super(InterWikiLink,self).__init__(tag, token, child_tags)
        self.delimiter1 = delimiter1
        self.delimiter2 = delimiter2
        self.regexp = re.compile(self.re_string())
        self.base_urls = base_urls
        self.links_funcs = links_funcs
        self.default_space_char = default_space_char
        self.space_chars = space_chars

    def re_string(self):
        wiki_id = r'(\w+)'
        optional_spaces = ' *'
        page_name = r'(\S+?( \S+?)*)' #allows any number of single spaces
        alias = r'(' + re.escape(self.delimiter2) + r' *(.*?))? *$'
        return wiki_id + optional_spaces + re.escape(self.delimiter1) + \
               optional_spaces + page_name + optional_spaces + \
               alias

    def page_name(self,mo):
        space_char = self.space_chars.get(mo.group(1),self.default_space_char)
        return mo.group(2).replace(' ',space_char)

    def href(self,mo):
        linktype = mo.group(1)
        base_url = self.base_urls.get(linktype)
        link_func = self.links_funcs.get(linktype)
        if not (link_func or base_url):
            return None
        else:
            href = self.page_name(mo)
            if link_func:
                href = link_func(href)
            if base_url:
                href = urlparse.urljoin(base_url, href)
            return href

    def _build(self,mo,element_store):
        if not self.href(mo):
            return '[[' + mo.group(0) + ']]'
        return bldr.tag.__getattr__(self.tag)(self.alias(mo,element_store),
                                              href=self.href(mo))
    def alias(self,mo,element_store):
        """Returns the string for the content of the Element."""
        if not mo.group(5):
            return ''.join([mo.group(1),self.delimiter1,mo.group(2)])
        else:
            return fragmentize(mo.group(5),self.child_tags,element_store)



class WikiLink(WikiElement):

    """Used to match wiki links inside a link.

    The search scope for these is only inside links.

    >>> wiki_link = WikiLink('a','',[],'|',base_url='http://somewiki.org/',
    ...                      space_char='_',class_func=None, path_func=None)
    >>> mo = wiki_link.regexp.search(" Home Page |Home")
    >>> wiki_link.href(mo)
    'http://somewiki.org/Home_Page'
    >>> wiki_link.alias(mo,{})
    ['Home']
    
    """

    def __init__(self, tag, token, child_tags,delimiter,
                 base_url,space_char,class_func,path_func):
        super(WikiLink,self).__init__(tag, token, child_tags)
        self.delimiter = delimiter
        self.base_url = base_url
        self.space_char = space_char
        self.class_func = class_func
        self.path_func = path_func
        self.regexp = re.compile(self.re_string())

    def re_string(self):
        optional_spaces = ' *'
        page_name = r'(\S+?( +\S+?)*?)' #allows any number of single spaces
        alias = r'(' + re.escape(self.delimiter) + r' *(.*?))? *$'
        return optional_spaces + page_name + optional_spaces + \
               alias

    def page_name(self,mo):
        return mo.group(1).replace(' ',self.space_char)
    
    def href(self,mo):
        if self.path_func:
            the_path = self.path_func(self.page_name(mo))
        else:
            the_path = self.page_name(mo)
        return urlparse.urljoin(self.base_url, the_path)

    def _build(self,mo,element_store):
        if self.class_func:
            the_class = self.class_func(self.page_name(mo))
        else:
            the_class = None
        return bldr.tag.__getattr__(self.tag)(self.alias(mo,element_store),
                                              href=self.href(mo),
                                              class_=the_class)
    
    def alias(self,mo,element_store):
        """Returns the string for the content of the Element."""
        if not mo.group(3):
            return mo.group(1)
        else:
            return fragmentize(mo.group(4),self.child_tags,element_store)




class BlockElement(WikiElement):

    """Block elements inherit form this class

    Wiki elements wanting ``append_newline = True`` should use this
    as the base also.

    """

    append_newline = True


class List(BlockElement):

    """Finds list (ordered, unordered, and definition) wiki elements.

    group(1) of the match object includes all lines from the list
    including newline characters.
        
    """

    def __init__(self, tag, token,child_tags,stop_tokens):
        super(List,self).__init__(tag, token, child_tags)
        self.stop_tokens = stop_tokens
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        """This re_string is for finding generic block elements like
        lists (ordered, unordered, and definition) that start with a
        single token.
        """
        leading_whitespace = r'^([ \t]*'
        only_one_token = re.escape(self.token)+'[^'+ re.escape(self.token) + ']'
        rest_of_list = r'.*?\n)'
##        only_one_other_token = re.escape(self.other_token)+'(?!'+ \
##                               re.escape(self.other_token) + ')'
        only_one_stop_token = '([' + re.escape(self.stop_tokens) + r'])(?!\3)'        
        look_ahead = '(?=([ \t]*' + only_one_stop_token + '|$))'
        return leading_whitespace + only_one_token + rest_of_list + \
               look_ahead


class ListItem(WikiElement):
    r"""Matches the current list item.

    Everything up to the next same-level list item is matched.

    >>> list_item = ListItem('li',[],'#*')
    >>> mo = list_item.regexp.search("*one\n**one.1\n**one.2\n*two\n")
    >>> mo.group(2)
    'one\n**one.1\n**one.2'
    >>> mo.group(0)
    '*one\n**one.1\n**one.2'
    
    """
    
    append_newline = False

    def __init__(self, tag, child_tags, list_tokens):
        """Constructor for list items.

        :parameters"
          list_tokens
            A string that includes the tokens used for lists
        """
        super(ListItem,self).__init__(tag, token=None,
                                      child_tags=child_tags)
        self.list_tokens = list_tokens
        self.regexp = re.compile(self.re_string(),re.DOTALL)

    def re_string(self):
        whitespace = r'[ \t]*'
        item_start = '([*#]+)'
        rest_of_item = r'(.*?)\n?'
        start_of_same_level_item = r'\1(?![*#])'
        look_ahead = r'(?=(\n' + whitespace + start_of_same_level_item + '|$))'
        return whitespace + item_start + whitespace + \
               rest_of_item + look_ahead

    def _build(self,mo,element_store):
        return bldr.tag.__getattr__(self.tag)(fragmentize(mo.group(2),
                                                          self.child_tags,
                                                          element_store))


class NestedList(WikiElement):

    r"""Finds a list in the current list item.

    >>> nested_ul = NestedList('ul','*',[])
    >>> mo = nested_ul.regexp.search('one\n**one.1\n**one.2\n')
    >>> mo.group(1)
    '**one.1\n**one.2\n'
    >>> mo.group(0) == mo.group(1)
    True

    """

    def __init__(self, tag, token,child_tags):
        super(NestedList,self).__init__(tag, token, child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        look_behind = r'(?<=\n)' # have to avoid finding a list on the first line
        whitespace = r'(\s*'
        rest_of_list = '.*$)'
        return look_behind + '^' + whitespace + re.escape(self.token) + \
               rest_of_list


class DefinitionTerm(BlockElement):

    r"""Processes definition terms.

    >>> term = DefinitionTerm('dt',';',[],stop_token=':')
    >>> mo1,mo2 = term.regexp.finditer(";term1\n:def1\n;term2:def2\n")
    >>> mo1.group(1), mo2.group(1)
    ('term1', 'term2')
    >>> mo1.group(0), mo2.group(0)
    (';term1\n', ';term2')

    group(1) of the match object is the term line or up to the first ':'
        
    """

    def __init__(self, tag, token,child_tags,stop_token):
        super(DefinitionTerm,self).__init__(tag, token, child_tags)
        self.stop_token = stop_token
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        leading_whitespace = r'^([ \t]*'
        #only_one_token = re.escape(self.token)+'[^'+ re.escape(self.token) + ']'
        rest_of_list = r'.*?\n)'
        #only_one_stop_token = '([' + re.escape(self.stop_tokens) + r'])(?!\3)'
        #look_ahead = r'(?=([ \t]*' + only_one_stop_token + '|$))'
        return r'^[ \t]*' + re.escape(self.token) + r'[ \t]*(.*?' + \
               re.escape(self.stop_token) +  '?)\s*(\n|(?=(' + \
               esc_neg_look + re.escape(self.stop_token) + r'|$)))'


class DefinitionDef(BlockElement):

    r"""Processes definitions.

    >>> definition = DefinitionDef('dd',':',[])
    >>> mo1,mo2 = definition.regexp.finditer(":def1a\ndef1b\n:def2\n")
    >>> mo1.group(1), mo2.group(1)
    ('def1a\ndef1b', 'def2')
    >>> mo1.group(0), mo2.group(0)
    (':def1a\ndef1b\n', ':def2\n')

    group(1) of the match object includes all lines from the defintion
    up to the next definition.
        
    """

    def __init__(self, tag, token,child_tags):
        super(DefinitionDef,self).__init__(tag, token, child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        leading_whitespace = r'^([ \t]*'
        rest_of_list = r'.*?\n)'
        look_ahead = r'(?=([ \t]*' + re.escape(self.token) + r')|$)'
        return r'^[ \t]*' + re.escape(self.token) + r'?[ \t]*(.+?)\s*\n(?=([ \t]*' + \
               re.escape(self.token) + r')|$)'


class Paragraph(BlockElement):

    """"This should be the last outer level wiki element to be "searched".

    Anything that is left over will be placed in paragraphs.

    """

    def __init__(self, tag, child_tags):
        super(Paragraph,self).__init__(tag,token=None, child_tags=child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        return r'^(.*)\n'


class Heading(BlockElement):

    r"""Finds heading wiki elements.

    >>> h1 = Heading('h1','=',[])
    >>> mo = h1.regexp.search('before\n = An important thing = \n after')
    >>> mo.group(1)
    'An important thing'
    >>> mo.group(0)
    ' = An important thing = \n'

    """
  
    def __init__(self, tag, token, child_tags):
        super(Heading,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        whitespace = r'[ \t]*'
        neg_look_ahead = '(?!' + re.escape(self.token[0]) + ')'
        content = '(.*?)'
        trailing_markup = '(' + re.escape(self.token[0]) + r'+[ \t]*)?\n'
        return '^' + whitespace + re.escape(self.token) + neg_look_ahead + \
               whitespace + content + whitespace + trailing_markup


class Table(BlockElement):

    r"""Find tables.

    >>> table = Table('table','|',[])
    >>> mo = table.regexp.search("before\n | one | two |\n|one|two \n hi")
    >>> mo.group(1)
    ' | one | two |\n|one|two \n'
    >>> mo.group(0) == mo.group(1)
    True
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(Table,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        whitespace = r'[ \t]*'
        rest_of_line = r'.*?\n'
        return '^((' + whitespace + re.escape(self.token) + \
               rest_of_line + ')+)'


class TableRow(BlockElement):

    r"""Finds rows in a table.

    >>> row = TableRow('tr','|',[])
    >>> mo = row.regexp.search(' | one | two |\n|one|two \n')
    >>> mo.group(1)
    '| one | two '
    >>> mo.group(0)
    ' | one | two |\n'
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(TableRow,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        whitespace = r'[ \t]*'
        content = '(' + re.escape(self.token) + '.*?)'
        trailing_token = re.escape(self.token) + '?'
        return '^' + whitespace + content + trailing_token + \
               whitespace + r'\n'


class TableCell(WikiElement):

    r"""Finds cells in a table row.

    >>> cell = TableCell('td','|',[])
    >>> mo = cell.regexp.search('| one | two ')
    >>> mo.group(1)
    'one'
    >>> mo.group(0)
    '| one '
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(TableCell,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string())

    def re_string(self):
        whitespace = r'[ \t]*'
        content = '(.*?)'
        look_ahead = '((?=' + esc_neg_look + re.escape(self.token[0]) + ')|$)'
        return esc_neg_look + re.escape(self.token) + whitespace + \
               content + whitespace + look_ahead    



class Link(InlineElement):

    """Finds and builds links."""
    
    def __init__(self, tag, token, child_tags):
        super(Link,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string())

    def _build(self,mo,element_store):

        link = fragmentize(mo.group(1),self.child_tags,element_store)

        if link:
            return bldr.tag(link)
        else:
            return token[0] + mo.group(0) + token[-1]

class Image(InlineElement):

    """Processes image elements.

    >>> img = Image('img',('{{','}}'),[], delimiter='|')
    >>> mo = img.regexp.search('{{ picture.jpg | An image of a house }}')
    >>> img._build(mo,{}).generate().render()
    '<img src="picture.jpg" alt="An image of a house"/>'

    """

    def __init__(self, tag, token, child_tags,delimiter):
        super(Image,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string())
        self.delimiter = delimiter
        self.src_regexp = re.compile(r'^\s*(\S+)\s*$')

    def _build(self,mo,element_store):
        body = mo.group(1).split(self.delimiter,1)
        src_mo = self.src_regexp.search(body[0])
        if not src_mo:
            return bldr.tag.span('Bad Image src')
        if sanitizer.is_safe_uri(src_mo.group(1)):
            link = src_mo.group(1)
        else:
            link = "unsafe_uri_detected"
        if len(body) == 1:
            alias = link
        else:
            alias = body[1].strip()
        return bldr.tag.__getattr__(self.tag)(src=link ,alt=alias)


class NoWikiElement(InlineElement):

    """Inline no-wiki.

    When two or more end tokens are found together, only last marks
    the end of the element.

    This element must be on a single line.
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(NoWikiElement,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL) 

    def _build(self,mo,element_store):
        if self.tag:
            return bldr.tag.__getattr__(self.tag)(
                   fragmentize(mo.group(1), self.child_tags,
                               element_store,
                               remove_escapes=False))
        else:
            return bldr.tag(fragmentize(mo.group(1),self.child_tags,
                                        element_store,
                                        remove_escapes=False))

    def re_string(self):
        if isinstance(self.token,str):
            content = '(.+?' + re.escape(self.token[-1]) + '*)'
            return esc_neg_look + re.escape(self.token) + \
                   content + re.escape(self.token)
        else:
            content = '(.+?' + re.escape(self.token[1][-1]) + '*)'
            return esc_neg_look + re.escape(self.token[0]) + \
                   content + re.escape(self.token[1])


class PreBlock(BlockElement):

    """A preformatted block.

    If a closing token is found on a line with a space as the first
    character, the space will be removed from the output.
    
    """

    def __init__(self, tag, token, child_tags=[]):
        super(PreBlock,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)
        self.regexp2 = re.compile(self.re_string2(),re.MULTILINE)

    def re_string(self):
        if isinstance(self.token,str):
            return '^' + re.escape(self.token) + r'\s*?\n(.*?\n)' + \
                   re.escape(self.token) + r'\s*?\n'
        else:
            start = '^' + re.escape(self.token[0]) + r'\s*?\n'
            content = r'(.+?\n)'
            end = re.escape(self.token[1]) + r'\s*?\n'
            return start + content + end

    def re_string2(self):
        """Finds a closing token with a space at the start of the line."""
        if isinstance(self.token,str):
            return r'^ (\s*?' + re.escape(self.token) + r'\s*?\n)'
        else:
            return r'^ (\s*?' + re.escape(self.token[1]) + r'\s*?\n)'

    def _build(self,mo,element_store):
        match = self.regexp2.sub(r'\1',mo.group(1))
        
        return bldr.tag.__getattr__(self.tag)(
            fragmentize(match,self.child_tags,
                        element_store,remove_escapes=False))


class LoneElement(BlockElement):

    """Element on a line by itself with no content (e.g., <hr/>)"""

    def __init__(self, tag, token, child_tags):
        super(LoneElement,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL+re.MULTILINE)

    def re_string(self):
        return r'^(\s*?' + re.escape(self.token) + r'\s*?\n)'

    def _build(self,mo,element_store):
        return bldr.tag.__getattr__(self.tag)()

class LonePlaceHolder(BlockElement):

    """A place holder on a line by itself or with other place holders.
    This is used to avoid these being enclosed in a paragraph.

    """
    append_newline = False
    def __init__(self, tag, token, child_tags):
        super(LonePlaceHolder,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        place_holder = re.escape(self.token[0]) + r'\S*?' + re.escape(self.token[1])
        return r'^\s*?(' + place_holder +   r'\s*$)+\s*?\n'

    def _build(self,mo,element_store):
        return bldr.tag(fragmentize(mo.group(0),[],element_store))
 
class BlankLine(WikiElement):

    """Blank lines divide elements but don't add any output."""

    def __init__(self):
        super(BlankLine,self).__init__(tag=None,token='' , child_tags=[])
        self.regexp = re.compile(self.re_string(),re.MULTILINE)

    def re_string(self):
        return r'^(\s*\n)+'
     
    def _build(self,mo,element_store):
        return None

    
class LineBreak(InlineElement):

    """An inline line break."""

    #append_newline = True
    def __init__(self,tag, token, child_tags=[]):
        super(LineBreak,self).__init__(tag,token , child_tags)
        self.regexp = re.compile(self.re_string(),re.DOTALL)

    def re_string(self):
        return esc_neg_look + re.escape(self.token)
    
    def _build(self,mo,element_store):
        return bldr.tag.__getattr__(self.tag)()



def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()    
