# -*- coding: utf-8 -*-
"""
    pygments.lexers.asm
    ~~~~~~~~~~~~~~~~~~~

    Lexers for assembly languages.

    :copyright: 2007 by Frits van Bommel.
    :license: BSD, see LICENSE for more details.
"""

import re
try:
    set
except NameError:
    from sets import Set as set

from pygments.lexer import RegexLexer, include, bygroups, using, \
                           this, DelegatingLexer
from pygments.lexers.compiled import DLexer, CppLexer, CLexer
from pygments.token import *

__all__ = ['GasLexer', 'ObjdumpLexer','DObjdumpLexer', 'CppObjdumpLexer',
           'CObjdumpLexer', 'LlvmLexer', 'NasmLexer']


class GasLexer(RegexLexer):
    """
    For Gas (AT&T) assembly code.
    """
    name = 'GAS'
    aliases = ['gas']
    filenames = ['*.s', '*.S']
    mimetypes = ['text/x-gas']

    #: optional Comment or Whitespace
    string = r'"(\\"|[^"])*"'
    char = r'[a-zA-Z$._0-9@]'
    identifier = r'(?:[a-zA-Z$_]' + char + '*|\.' + char + '+)'
    number = r'(?:0[xX][a-zA-Z0-9]+|\d+)'

    tokens = {
        'root': [
            include('whitespace'),
            (identifier + ':', Name.Label),
            (r'\.' + identifier, Name.Attribute, 'directive-args'),
            (r'lock|rep(n?z)?|data\d+', Name.Attribute),
            (identifier, Name.Function, 'instruction-args'),
            (r'[\r\n]+', Text)
        ],
        'directive-args': [
            (identifier, Name.Constant),
            (string, String),
            ('@' + identifier, Name.Attribute),
            (number, Number.Integer),
            (r'[\r\n]+', Text, '#pop'),

            (r'#.*?$', Comment, '#pop'),

            include('punctuation'),
            include('whitespace')
        ],
        'instruction-args': [
            # For objdump-disassembled code, shouldn't occur in
            # actual assembler input
            ('([a-z0-9]+)( )(<)('+identifier+')(>)',
                bygroups(Number.Hex, Text, Punctuation, Name.Constant,
                         Punctuation)),
            ('([a-z0-9]+)( )(<)('+identifier+')([-+])('+number+')(>)',
                bygroups(Number.Hex, Text, Punctuation, Name.Constant,
                         Punctuation, Number.Integer, Punctuation)),

            # Address constants
            (identifier, Name.Constant),
            (number, Number.Integer),
            # Registers
            ('%' + identifier, Name.Variable),
            # Numeric constants
            ('$'+number, Number.Integer),
            (r'[\r\n]+', Text, '#pop'),
            (r'#.*?$', Comment, '#pop'),
            include('punctuation'),
            include('whitespace')
        ],
        'whitespace': [
            (r'\n', Text),
            (r'\s+', Text),
            (r'#.*?\n', Comment)
        ],
        'punctuation': [
            (r'[-*,.():]+', Punctuation)
        ]
    }


class ObjdumpLexer(RegexLexer):
    """
    For the output of 'objdump -dr'
    """
    name = 'objdump'
    aliases = ['objdump']
    filenames = ['*.objdump']
    mimetypes = ['text/x-objdump']

    hex = r'[0-9A-Za-z]'

    tokens = {
        'root': [
            # File name & format:
            ('(.*?)(:)( +file format )(.*?)$',
                bygroups(Name.Label, Punctuation, Text, String)),
            # Section header
            ('(Disassembly of section )(.*?)(:)$',
                bygroups(Text, Name.Label, Punctuation)),
            # Function labels
            # (With offset)
            ('('+hex+'+)( )(<)(.*?)([-+])(0[xX][A-Za-z0-9]+)(>:)$',
                bygroups(Number.Hex, Text, Punctuation, Name.Function,
                         Punctuation, Number.Hex, Punctuation)),
            # (Without offset)
            ('('+hex+'+)( )(<)(.*?)(>:)$',
                bygroups(Number.Hex, Text, Punctuation, Name.Function,
                         Punctuation)),
            # Code line with disassembled instructions
            ('( *)('+hex+r'+:)(\t)((?:'+hex+hex+' )+)( *\t)([a-zA-Z].*?)$',
                bygroups(Text, Name.Label, Text, Number.Hex, Text,
                         using(GasLexer))),
            # Code line with ascii
            ('( *)('+hex+r'+:)(\t)((?:'+hex+hex+' )+)( *)(.*?)$',
                bygroups(Text, Name.Label, Text, Number.Hex, Text, String)),
            # Continued code line, only raw opcodes without disassembled
            # instruction
            ('( *)('+hex+r'+:)(\t)((?:'+hex+hex+' )+)$',
                bygroups(Text, Name.Label, Text, Number.Hex)),
            # Skipped a few bytes
            ('\t\.\.\.$', Text),
            # Relocation line
            # (With offset)
            ('(\t\t\t)('+hex+'+:)( )([^\t]+)(\t)(.*?)([-+])(0x' + hex + '+)$',
                bygroups(Text, Name.Label, Text, Name.Property, Text,
                         Name.Constant, Punctuation, Number.Hex)),
            # (Without offset)
            ('(\t\t\t)('+hex+'+:)( )([^\t]+)(\t)(.*?)$',
                bygroups(Text, Name.Label, Text, Name.Property, Text,
                         Name.Constant)),
            ('[^\n]+\n', Other)
        ]
    }


class DObjdumpLexer(DelegatingLexer):
    """
    For the output of 'objdump -Sr on compiled D files'
    """
    name = 'd-objdump'
    aliases = ['d-objdump']
    filenames = ['*.d-objdump']
    mimetypes = ['text/x-d-objdump']

    def __init__(self, **options):
        super(DObjdumpLexer, self).__init__(DLexer, ObjdumpLexer, **options)


class CppObjdumpLexer(DelegatingLexer):
    """
    For the output of 'objdump -Sr on compiled C++ files'
    """
    name = 'cpp-objdump'
    aliases = ['cpp-objdump', 'c++-objdumb', 'cxx-objdump']
    filenames = ['*.cpp-objdump', '*.c++-objdump', '*.cxx-objdump']
    mimetypes = ['text/x-cpp-objdump']

    def __init__(self, **options):
        super(CppObjdumpLexer, self).__init__(CppLexer, ObjdumpLexer, **options)


class CObjdumpLexer(DelegatingLexer):
    """
    For the output of 'objdump -Sr on compiled C files'
    """
    name = 'c-objdump'
    aliases = ['c-objdump']
    filenames = ['*.c-objdump']
    mimetypes = ['text/x-c-objdump']

    def __init__(self, **options):
        super(CObjdumpLexer, self).__init__(CLexer, ObjdumpLexer, **options)


class LlvmLexer(RegexLexer):
    """
    For LLVM assembly code.
    """
    name = 'LLVM'
    aliases = ['llvm']
    filenames = ['*.ll']
    mimetypes = ['text/x-llvm']

    #: optional Comment or Whitespace
    string = r'"[^"]*?"'
    identifier = r'([a-zA-Z$._][a-zA-Z$._0-9]*|' + string + ')'

    tokens = {
        'root': [
            include('whitespace'),

            # Before keywords, because keywords are valid label names :(...
            (r'^\s*' + identifier + '\s*:', Name.Label),

            include('keyword'),

            (r'%' + identifier, Name.Variable),#Name.Identifier.Local),
            (r'@' + identifier, Name.Constant),#Name.Identifier.Global),
            (r'%\d+', Name.Variable.Anonymous),#Name.Identifier.Anonymous),
            (r'c?' + string, String),

            (r'0[xX][a-fA-F0-9]+', Number),
            (r'-?\d+(?:[.]\d+)?(?:[eE][-+]?\d+(?:[.]\d+)?)?', Number),

            (r'[=<>{}\[\]()*.,]|x\b', Punctuation)
        ],
        'whitespace': [
            (r'(\n|\s)+', Text),
            (r';.*?\n', Comment)
        ],
        'keyword': [
            # Regular keywords
            (r'(void|label|float|double|opaque'
             r'|to'
             r'|alias|type'
             r'|zeroext|signext|inreg|sret|noalias|noreturn|nounwind|nest'
             r'|module|asm|target|datalayout|triple'
             r'|true|false|null|zeroinitializer|undef'
             r'|global|internal|external|linkonce|weak|appending|extern_weak'
             r'|dllimport|dllexport'
             r'|ccc|fastcc|coldcc|cc|tail'
             r'|default|hidden|protected'
             r'|thread_local|constant|align|section'
             r'|define|declare'

             # Statements & expressions
             r'|trunc|zext|sext|fptrunc|fpext|fptoui|fptosi|uitofp|sitofp'
             r'|ptrtoint|inttoptr|bitcast|getelementptr|select|icmp|fcmp'
             r'|extractelement|insertelement|shufflevector'
             r'|sideeffect|volatile'
             r'|ret|br|switch|invoke|unwind|unreachable'
             r'|add|sub|mul|udiv|sdiv|fdiv|urem|srem|frem'
             r'|shl|lshr|ashr|and|or|xor'
             r'|malloc|free|alloca|load|store'
             r'|phi|call|va_arg|va_list'

             # Comparison condition codes for icmp
             r'|eq|ne|ugt|uge|ult|ule|sgt|sge|slt|sle'
             # Ditto for fcmp: (minus keywords mentioned in other contexts)
             r'|oeq|ogt|oge|olt|ole|one|ord|ueq|ugt|uge|une|uno'

             r')\b', Keyword),
            # Integer types
            (r'i[1-9]\d*', Keyword)
        ]
    }


class NasmLexer(RegexLexer):
    """
    For Nasm (Intel) assembly code.
    """
    name = 'NASM'
    aliases = ['nasm']
    filenames = ['*.asm', '*.ASM']
    mimetypes = ['text/x-nasm']

    identifier = r'[a-zA-Z$._?][a-zA-Z0-9$._?#@~]*'
    hexn = r'(?:0[xX][0-9a-fA-F]+|$0[0-9a-fA-F]*|[0-9a-fA-F]+h)'
    octn = r'[0-7]+q'
    binn = r'[01]+b'
    decn = r'[0-9]+'
    floatn = decn + r'\.e?' + decn
    string = r'"(\\"|[^"])*"|' + r"'(\\'|[^'])*'"
    declkw = r'(?:res|d)[bwdqt]|times'
    register = (r'[a-d][lh]|e?[a-d]x|e?[sb]p|e?[sd]i|[c-gs]s|st[0-7]|'
                r'mm[0-7]|cr[0-4]|dr[0-367]|tr[3-7]')
    wordop = r'seg|wrt|strict'
    type = r'byte|[dq]?word'
    directives = (r'BITS|USE16|USE32|SECTION|SEGMENT|ABSOLUTE|EXTERN|GLOBAL|'
                  r'COMMON|CPU|GROUP|UPPERCASE|IMPORT|EXPORT|LIBRARY|MODULE')

    flags = re.IGNORECASE | re.MULTILINE
    tokens = {
        'root': [
            include('whitespace'),
            (r'^\s*%', Comment.Preproc, 'preproc'),
            (identifier + ':', Name.Label),
            (directives, Keyword, 'instruction-args'),
            (r'(%s)\s+(equ)' % identifier,
                bygroups(Name.Constant, Keyword.Declaration),
                'instruction-args'),
            (declkw, Keyword.Declaration, 'instruction-args'),
            (identifier, Name.Function, 'instruction-args'),
            (r'[\r\n]+', Text)
        ],
        'instruction-args': [
            (string, String),
            (hexn, Number.Hex),
            (octn, Number.Oct),
            (binn, Number),
            (floatn, Number.Float),
            (decn, Number.Integer),
            include('punctuation'),
            (register, Name.Builtin),
            (identifier, Name.Variable),
            (r'[\r\n]+', Text, '#pop'),
            include('whitespace')
        ],
        'preproc': [
            (r'[^;\n]+', Comment.Preproc),
            (r';.*?\n', Comment.Single, '#pop'),
            (r'\n', Comment.Preproc, '#pop'),
        ],
        'whitespace': [
            (r'\n', Text),
            (r'[ \t]+', Text),
            (r';.*', Comment.Single)
        ],
        'punctuation': [
            (r'[,():\[\]]+', Punctuation),
            (r'[&|^<>+*/%~-]+', Operator),
            (r'[$]+', Keyword.Constant),
            (wordop, Operator.Word),
            (type, Keyword.Type)
        ],
    }
