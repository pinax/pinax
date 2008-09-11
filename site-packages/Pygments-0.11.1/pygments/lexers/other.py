# -*- coding: utf-8 -*-
"""
    pygments.lexers.other
    ~~~~~~~~~~~~~~~~~~~~~

    Lexers for other languages.

    :copyright: 2006-2008 by Georg Brandl, Tim Hatch <tim@timhatch.com>,
                Stou Sandalski, Paulo Moura, Clara Dimene.
    :license: BSD, see LICENSE for more details.
"""

import re

from pygments.lexer import Lexer, RegexLexer, include, bygroups, using, this, \
                           do_insertions
from pygments.token import Error, Punctuation, \
     Text, Comment, Operator, Keyword, Name, String, Number, Generic
from pygments.util import shebang_matches


__all__ = ['SqlLexer', 'MySqlLexer', 'SqliteConsoleLexer', 'BrainfuckLexer',
           'BashLexer', 'BatchLexer', 'BefungeLexer', 'RedcodeLexer',
           'MOOCodeLexer', 'SmalltalkLexer', 'TcshLexer', 'LogtalkLexer',
           'GnuplotLexer', 'PovrayLexer']

line_re  = re.compile('.*?\n')


class SqlLexer(RegexLexer):
    """
    Lexer for Structured Query Language. Currently, this lexer does
    not recognize any special syntax except ANSI SQL.
    """

    name = 'SQL'
    aliases = ['sql']
    filenames = ['*.sql']
    mimetypes = ['text/x-sql']

    flags = re.IGNORECASE
    tokens = {
        'root': [
            (r'\s+', Text),
            (r'--.*?\n', Comment.Single),
            (r'/\*', Comment.Multiline, 'multiline-comments'),
            (r'(ABORT|ABS|ABSOLUTE|ACCESS|ADA|ADD|ADMIN|AFTER|AGGREGATE|'
             r'ALIAS|ALL|ALLOCATE|ALTER|ANALYSE|ANALYZE|AND|ANY|ARE|AS|'
             r'ASC|ASENSITIVE|ASSERTION|ASSIGNMENT|ASYMMETRIC|AT|ATOMIC|'
             r'AUTHORIZATION|AVG|BACKWARD|BEFORE|BEGIN|BETWEEN|BITVAR|'
             r'BIT_LENGTH|BOTH|BREADTH|BY|C|CACHE|CALL|CALLED|CARDINALITY|'
             r'CASCADE|CASCADED|CASE|CAST|CATALOG|CATALOG_NAME|CHAIN|'
             r'CHARACTERISTICS|CHARACTER_LENGTH|CHARACTER_SET_CATALOG|'
             r'CHARACTER_SET_NAME|CHARACTER_SET_SCHEMA|CHAR_LENGTH|CHECK|'
             r'CHECKED|CHECKPOINT|CLASS|CLASS_ORIGIN|CLOB|CLOSE|CLUSTER|'
             r'COALSECE|COBOL|COLLATE|COLLATION|COLLATION_CATALOG|'
             r'COLLATION_NAME|COLLATION_SCHEMA|COLUMN|COLUMN_NAME|'
             r'COMMAND_FUNCTION|COMMAND_FUNCTION_CODE|COMMENT|COMMIT|'
             r'COMMITTED|COMPLETION|CONDITION_NUMBER|CONNECT|CONNECTION|'
             r'CONNECTION_NAME|CONSTRAINT|CONSTRAINTS|CONSTRAINT_CATALOG|'
             r'CONSTRAINT_NAME|CONSTRAINT_SCHEMA|CONSTRUCTOR|CONTAINS|'
             r'CONTINUE|CONVERSION|CONVERT|COPY|CORRESPONTING|COUNT|'
             r'CREATE|CREATEDB|CREATEUSER|CROSS|CUBE|CURRENT|CURRENT_DATE|'
             r'CURRENT_PATH|CURRENT_ROLE|CURRENT_TIME|CURRENT_TIMESTAMP|'
             r'CURRENT_USER|CURSOR|CURSOR_NAME|CYCLE|DATA|DATABASE|'
             r'DATETIME_INTERVAL_CODE|DATETIME_INTERVAL_PRECISION|DAY|'
             r'DEALLOCATE|DECLARE|DEFAULT|DEFAULTS|DEFERRABLE|DEFERRED|'
             r'DEFINED|DEFINER|DELETE|DELIMITER|DELIMITERS|DEREF|DESC|'
             r'DESCRIBE|DESCRIPTOR|DESTROY|DESTRUCTOR|DETERMINISTIC|'
             r'DIAGNOSTICS|DICTIONARY|DISCONNECT|DISPATCH|DISTINCT|DO|'
             r'DOMAIN|DROP|DYNAMIC|DYNAMIC_FUNCTION|DYNAMIC_FUNCTION_CODE|'
             r'EACH|ELSE|ENCODING|ENCRYPTED|END|END-EXEC|EQUALS|ESCAPE|EVERY|'
             r'EXCEPT|ESCEPTION|EXCLUDING|EXCLUSIVE|EXEC|EXECUTE|EXISTING|'
             r'EXISTS|EXPLAIN|EXTERNAL|EXTRACT|FALSE|FETCH|FINAL|FIRST|FOR|'
             r'FORCE|FOREIGN|FORTRAN|FORWARD|FOUND|FREE|FREEZE|FROM|FULL|'
             r'FUNCTION|G|GENERAL|GENERATED|GET|GLOBAL|GO|GOTO|GRANT|GRANTED|'
             r'GROUP|GROUPING|HANDLER|HAVING|HIERARCHY|HOLD|HOST|IDENTITY|'
             r'IGNORE|ILIKE|IMMEDIATE|IMMUTABLE|IMPLEMENTATION|IMPLICIT|IN|'
             r'INCLUDING|INCREMENT|INDEX|INDITCATOR|INFIX|INHERITS|INITIALIZE|'
             r'INITIALLY|INNER|INOUT|INPUT|INSENSITIVE|INSERT|INSTANTIABLE|'
             r'INSTEAD|INTERSECT|INTO|INVOKER|IS|ISNULL|ISOLATION|ITERATE|JOIN|'
             r'K|KEY|KEY_MEMBER|KEY_TYPE|LANCOMPILER|LANGUAGE|LARGE|LAST|'
             r'LATERAL|LEADING|LEFT|LENGTH|LESS|LEVEL|LIKE|LILMIT|LISTEN|LOAD|'
             r'LOCAL|LOCALTIME|LOCALTIMESTAMP|LOCATION|LOCATOR|LOCK|LOWER|M|'
             r'MAP|MATCH|MAX|MAXVALUE|MESSAGE_LENGTH|MESSAGE_OCTET_LENGTH|'
             r'MESSAGE_TEXT|METHOD|MIN|MINUTE|MINVALUE|MOD|MODE|MODIFIES|'
             r'MODIFY|MONTH|MORE|MOVE|MUMPS|NAMES|NATIONAL|NATURAL|NCHAR|'
             r'NCLOB|NEW|NEXT|NO|NOCREATEDB|NOCREATEUSER|NONE|NOT|NOTHING|'
             r'NOTIFY|NOTNULL|NULL|NULLABLE|NULLIF|OBJECT|OCTET_LENGTH|OF|OFF|'
             r'OFFSET|OIDS|OLD|ON|ONLY|OPEN|OPERATION|OPERATOR|OPTION|OPTIONS|'
             r'OR|ORDER|ORDINALITY|OUT|OUTER|OUTPUT|OVERLAPS|OVERLAY|OVERRIDING|'
             r'OWNER|PAD|PARAMETER|PARAMETERS|PARAMETER_MODE|PARAMATER_NAME|'
             r'PARAMATER_ORDINAL_POSITION|PARAMETER_SPECIFIC_CATALOG|'
             r'PARAMETER_SPECIFIC_NAME|PARAMATER_SPECIFIC_SCHEMA|PARTIAL|'
             r'PASCAL|PENDANT|PLACING|PLI|POSITION|POSTFIX|PRECISION|PREFIX|'
             r'PREORDER|PREPARE|PRESERVE|PRIMARY|PRIOR|PRIVILEGES|PROCEDURAL|'
             r'PROCEDURE|PUBLIC|READ|READS|RECHECK|RECURSIVE|REF|REFERENCES|'
             r'REFERENCING|REINDEX|RELATIVE|RENAME|REPEATABLE|REPLACE|RESET|'
             r'RESTART|RESTRICT|RESULT|RETURN|RETURNED_LENGTH|'
             r'RETURNED_OCTET_LENGTH|RETURNED_SQLSTATE|RETURNS|REVOKE|RIGHT|'
             r'ROLE|ROLLBACK|ROLLUP|ROUTINE|ROUTINE_CATALOG|ROUTINE_NAME|'
             r'ROUTINE_SCHEMA|ROW|ROWS|ROW_COUNT|RULE|SAVE_POINT|SCALE|SCHEMA|'
             r'SCHEMA_NAME|SCOPE|SCROLL|SEARCH|SECOND|SECURITY|SELECT|SELF|'
             r'SENSITIVE|SERIALIZABLE|SERVER_NAME|SESSION|SESSION_USER|SET|'
             r'SETOF|SETS|SHARE|SHOW|SIMILAR|SIMPLE|SIZE|SOME|SOURCE|SPACE|'
             r'SPECIFIC|SPECIFICTYPE|SPECIFIC_NAME|SQL|SQLCODE|SQLERROR|'
             r'SQLEXCEPTION|SQLSTATE|SQLWARNINIG|STABLE|START|STATE|STATEMENT|'
             r'STATIC|STATISTICS|STDIN|STDOUT|STORAGE|STRICT|STRUCTURE|STYPE|'
             r'SUBCLASS_ORIGIN|SUBLIST|SUBSTRING|SUM|SYMMETRIC|SYSID|SYSTEM|'
             r'SYSTEM_USER|TABLE|TABLE_NAME| TEMP|TEMPLATE|TEMPORARY|TERMINATE|'
             r'THAN|THEN|TIMESTAMP|TIMEZONE_HOUR|TIMEZONE_MINUTE|TO|TOAST|'
             r'TRAILING|TRANSATION|TRANSACTIONS_COMMITTED|'
             r'TRANSACTIONS_ROLLED_BACK|TRANSATION_ACTIVE|TRANSFORM|'
             r'TRANSFORMS|TRANSLATE|TRANSLATION|TREAT|TRIGGER|TRIGGER_CATALOG|'
             r'TRIGGER_NAME|TRIGGER_SCHEMA|TRIM|TRUE|TRUNCATE|TRUSTED|TYPE|'
             r'UNCOMMITTED|UNDER|UNENCRYPTED|UNION|UNIQUE|UNKNOWN|UNLISTEN|'
             r'UNNAMED|UNNEST|UNTIL|UPDATE|UPPER|USAGE|USER|'
             r'USER_DEFINED_TYPE_CATALOG|USER_DEFINED_TYPE_NAME|'
             r'USER_DEFINED_TYPE_SCHEMA|USING|VACUUM|VALID|VALIDATOR|VALUES|'
             r'VARIABLE|VERBOSE|VERSION|VIEW|VOLATILE|WHEN|WHENEVER|WHERE|'
             r'WITH|WITHOUT|WORK|WRITE|YEAR|ZONE)\b', Keyword),
            (r'(ARRAY|BIGINT|BINARY|BIT|BLOB|BOOLEAN|CHAR|CHARACTER|DATE|'
             r'DEC|DECIMAL|FLOAT|INT|INTEGER|INTERVAL|NUMBER|NUMERIC|REAL|'
             r'SERIAL|SMALLINT|VARCHAR|VARYING|INT8|SERIAL8|TEXT)\b',
             Name.Builtin),
            (r'[+*/<>=~!@#%^&|`?^-]', Operator),
            (r'[0-9]+', Number.Integer),
            # TODO: Backslash escapes?
            (r"'(''|[^'])*'", String.Single),
            (r'"(""|[^"])*"', String.Symbol), # not a real string literal in ANSI SQL
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
            (r'[;:()\[\],\.]', Punctuation)
        ],
        'multiline-comments': [
            (r'/\*', Comment.Multiline, 'multiline-comments'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[^/\*]+', Comment.Multiline),
            (r'[/*]', Comment.Multiline)
        ]
    }


class MySqlLexer(RegexLexer):
    """
    Special lexer for MySQL.
    """

    name = 'MySQL'
    aliases = ['mysql']
    mimetypes = ['text/x-mysql']

    flags = re.IGNORECASE
    tokens = {
        'root': [
            (r'\s+', Text),
            (r'(#|--\s+).*?\n', Comment.Single),
            (r'/\*', Comment.Multiline, 'multiline-comments'),
            (r'[0-9]+', Number.Integer),
            (r'[0-9]*\.[0-9]+(e[+-][0-9]+)', Number.Float),
            # TODO: add backslash escapes
            (r"'(''|[^'])*'", String.Single),
            (r'"(""|[^"])*"', String.Double),
            (r"`(``|[^`])*`", String.Symbol),
            (r'[+*/<>=~!@#%^&|`?^-]', Operator),
            (r'\b(tinyint|smallint|mediumint|int|integer|bigint|date|'
             r'datetime|time|bit|bool|tinytext|mediumtext|longtext|text|'
             r'tinyblob|mediumblob|longblob|blob|float|double|double\s+'
             r'precision|real|numeric|dec|decimal|timestamp|year|char|'
             r'varchar|varbinary|varcharacter|enum|set)(\b\s*)(\()?',
             bygroups(Keyword.Type, Text, Punctuation)),
            (r'\b(add|all|alter|analyze|and|as|asc|asensitive|before|between|'
             r'bigint|binary|blob|both|by|call|cascade|case|change|char|'
             r'character|check|collate|column|condition|constraint|continue|'
             r'convert|create|cross|current_date|current_time|'
             r'current_timestamp|current_user|cursor|database|databases|'
             r'day_hour|day_microsecond|day_minute|day_second|dec|decimal|'
             r'declare|default|delayed|delete|desc|describe|deterministic|'
             r'distinct|distinctrow|div|double|drop|dual|each|else|elseif|'
             r'enclosed|escaped|exists|exit|explain|fetch|float|float4|float8'
             r'|for|force|foreign|from|fulltext|grant|group|having|'
             r'high_priority|hour_microsecond|hour_minute|hour_second|if|'
             r'ignore|in|index|infile|inner|inout|insensitive|insert|int|'
             r'int1|int2|int3|int4|int8|integer|interval|into|is|iterate|'
             r'join|key|keys|kill|leading|leave|left|like|limit|lines|load|'
             r'localtime|localtimestamp|lock|long|loop|low_priority|match|'
             r'minute_microsecond|minute_second|mod|modifies|natural|'
             r'no_write_to_binlog|not|numeric|on|optimize|option|optionally|'
             r'or|order|out|outer|outfile|precision|primary|procedure|purge|'
             r'raid0|read|reads|real|references|regexp|release|rename|repeat|'
             r'replace|require|restrict|return|revoke|right|rlike|schema|'
             r'schemas|second_microsecond|select|sensitive|separator|set|'
             r'show|smallint|soname|spatial|specific|sql|sql_big_result|'
             r'sql_calc_found_rows|sql_small_result|sqlexception|sqlstate|'
             r'sqlwarning|ssl|starting|straight_join|table|terminated|then|'
             r'to|trailing|trigger|undo|union|unique|unlock|unsigned|update|'
             r'usage|use|using|utc_date|utc_time|utc_timestamp|values|'
             r'varying|when|where|while|with|write|x509|xor|year_month|'
             r'zerofill)\b', Keyword),
            # TODO: this list is not complete
            (r'\b(auto_increment|engine|charset|tables)\b', Keyword.Pseudo),
            (r'(true|false|null)', Name.Constant),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(\()',
             bygroups(Name.Function, Text, Punctuation)),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
            (r'@[A-Za-z0-9]*[._]*[A-Za-z0-9]*', Name.Variable),
            (r'[;:()\[\],\.]', Punctuation)
        ],
        'multiline-comments': [
            (r'/\*', Comment.Multiline, 'multiline-comments'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[^/\*]+', Comment.Multiline),
            (r'[/*]', Comment.Multiline)
        ]
    }


class SqliteConsoleLexer(Lexer):
    """
    Lexer for example sessions using sqlite3.

    *New in Pygments 0.11.*
    """

    name = 'sqlite3con'
    aliases = ['sqlite3']
    filenames = ['*.sqlite3-console']
    mimetypes = ['text/x-sqlite3-console']

    def get_tokens_unprocessed(self, data):
        sql = SqlLexer(**self.options)

        curcode = ''
        insertions = []
        for match in line_re.finditer(data):
            line = match.group()
            if line.startswith('sqlite> ') or line.startswith('   ...> '):
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, line[:8])]))
                curcode += line[8:]
            else:
                if curcode:
                    for item in do_insertions(insertions,
                                              sql.get_tokens_unprocessed(curcode)):
                        yield item
                    curcode = ''
                    insertions = []
                if line.startswith('SQL error: '):
                    yield (match.start(), Generic.Traceback, line)
                else:
                    yield (match.start(), Generic.Output, line)
        if curcode:
            for item in do_insertions(insertions,
                                      sql.get_tokens_unprocessed(curcode)):
                yield item


class BrainfuckLexer(RegexLexer):
    """
    Lexer for the esoteric `BrainFuck <http://www.muppetlabs.com/~breadbox/bf/>`_
    language.
    """

    name = 'Brainfuck'
    aliases = ['brainfuck', 'bf']
    filenames = ['*.bf', '*.b']
    mimetypes = ['application/x-brainfuck']

    tokens = {
        'common': [
            # use different colors for different instruction types
            (r'[.,]+', Name.Tag),
            (r'[+-]+', Name.Builtin),
            (r'[<>]+', Name.Variable),
            (r'[^.,+\-<>\[\]]+', Comment),
        ],
        'root': [
            (r'\[', Keyword, 'loop'),
            (r'\]', Error),
            include('common'),
        ],
        'loop': [
            (r'\[', Keyword, '#push'),
            (r'\]', Keyword, '#pop'),
            include('common'),
        ]
    }


class BefungeLexer(RegexLexer):
    """
    Lexer for the esoteric `Befunge <http://en.wikipedia.org/wiki/Befunge>`_
    language.

    *New in Pygments 0.7.*
    """
    name = 'Befunge'
    aliases = ['befunge']
    filenames = ['*.befunge']
    mimetypes = ['application/x-befunge']

    tokens = {
        'root': [
            (r'[0-9a-f]', Number),
            (r'[\+\*/%!`-]', Operator), # Traditional math
            (r'[<>^v?\[\]rxjk]', Name.Variable), # Move, imperatives
            (r'[:\\$.,n]', Name.Builtin), # Stack ops, imperatives
            (r'[|_mw]', Keyword),
            (r'[{}]', Name.Tag), # Befunge-98 stack ops
            (r'".*?"', String.Double), # Strings don't appear to allow escapes
            (r'\'.', String.Single), # Single character
            (r'[#;]', Comment), # Trampoline... depends on direction hit
            (r'[pg&~=@iotsy]', Keyword), # Misc
            (r'[()A-Z]', Comment), # Fingerprints
            (r'\s+', Text), # Whitespace doesn't matter
        ],
    }


class BashLexer(RegexLexer):
    """
    Lexer for (ba)sh shell scripts.

    *New in Pygments 0.6.*
    """

    name = 'Bash'
    aliases = ['bash', 'sh']
    filenames = ['*.sh']
    mimetypes = ['application/x-sh', 'application/x-shellscript']

    tokens = {
        'root': [
            include('basic'),
            (r'\$\(\(', Keyword, 'math'),
            (r'\$\(', Keyword, 'paren'),
            (r'\${#?', Keyword, 'curly'),
            (r'`', String.Backtick, 'backticks'),
            include('data'),
        ],
        'basic': [
            (r'\b(if|fi|else|while|do|done|for|then|return|function|case|'
             r'select|continue|until|esac|elif)\s*\b',
             Keyword),
            (r'\b(alias|bg|bind|break|builtin|caller|cd|command|compgen|'
             r'complete|declare|dirs|disown|echo|enable|eval|exec|exit|'
             r'export|false|fc|fg|getopts|hash|help|history|jobs|kill|let|'
             r'local|logout|popd|printf|pushd|pwd|read|readonly|set|shift|'
             r'shopt|source|suspend|test|time|times|trap|true|type|typeset|'
             r'ulimit|umask|unalias|unset|wait)\s*\b',
             Name.Builtin),
            (r'#.*\n', Comment),
            (r'\\[\w\W]', String.Escape),
            (r'(\b\w+)(\s*)(=)', bygroups(Name.Variable, Text, Operator)),
            (r'[\[\]{}()=]+', Operator),
            (r'<<\s*(\'?)\\?(\w+)[\w\W]+?\2', String),
            (r'&&|\|\|', Operator),
        ],
        'data': [
            (r'\$?"(\\\\|\\[0-7]+|\\.|[^"])*"', String.Double),
            (r"\$?'(\\\\|\\[0-7]+|\\.|[^'])*'", String.Single),
            (r';', Text),
            (r'\s+', Text),
            (r'[^=\s\n\[\]{}()$"\'`\\<]+', Text),
            (r'\d+(?= |\Z)', Number),
            (r'\$#?(\w+|.)', Name.Variable),
            (r'<', Text),
        ],
        'curly': [
            (r'}', Keyword, '#pop'),
            (r':-', Keyword),
            (r'[a-zA-Z0-9_]+', Name.Variable),
            (r'[^}:"\'`$]+', Punctuation),
            (r':', Punctuation),
            include('root'),
        ],
        'paren': [
            (r'\)', Keyword, '#pop'),
            include('root'),
        ],
        'math': [
            (r'\)\)', Keyword, '#pop'),
            (r'[-+*/%^|&]|\*\*|\|\|', Operator),
            (r'\d+', Number),
            include('root'),
        ],
        'backticks': [
            (r'`', String.Backtick, '#pop'),
            include('root'),
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'(ba|z|)sh')


class BatchLexer(RegexLexer):
    """
    Lexer for the DOS/Windows Batch file format.

    *New in Pygments 0.7.*
    """
    name = 'Batchfile'
    aliases = ['bat']
    filenames = ['*.bat', '*.cmd']
    mimetypes = ['application/x-dos-batch']

    flags = re.MULTILINE | re.IGNORECASE

    tokens = {
        'root': [
            # Lines can start with @ to prevent echo
            (r'^\s*@', Punctuation),
            (r'^(\s*)(rem\s.*)$', bygroups(Text, Comment)),
            (r'".*?"', String.Double),
            (r"'.*?'", String.Single),
            # If made more specific, make sure you still allow expansions
            # like %~$VAR:zlt
            (r'%%?[~$:\w]+%?', Name.Variable),
            (r'::.*', Comment), # Technically :: only works at BOL
            (r'(set)(\s+)(\w+)', bygroups(Keyword, Text, Name.Variable)),
            (r'(call)(\s+)(:\w+)', bygroups(Keyword, Text, Name.Label)),
            (r'(goto)(\s+)(\w+)', bygroups(Keyword, Text, Name.Label)),
            (r'\b(set|call|echo|on|off|endlocal|for|do|goto|if|pause|'
             r'setlocal|shift|errorlevel|exist|defined|cmdextversion|'
             r'errorlevel|else|cd|md|del|deltree|cls|choice)\b', Keyword),
            (r'\b(equ|neq|lss|leq|gtr|geq)\b', Operator),
            include('basic'),
            (r'.', Text),
        ],
        'echo': [
            # Escapes only valid within echo args?
            (r'\^\^|\^<|\^>|\^\|', String.Escape),
            (r'\n', Text, '#pop'),
            include('basic'),
            (r'[^\'"^]+', Text),
        ],
        'basic': [
            (r'".*?"', String.Double),
            (r"'.*?'", String.Single),
            (r'`.*?`', String.Backtick),
            (r'-?\d+', Number),
            (r',', Punctuation),
            (r'=', Operator),
            (r'/\S+', Name),
            (r':\w+', Name.Label),
            (r'\w:\w+', Text),
            (r'([<>|])(\s*)(\w+)', bygroups(Punctuation, Text, Name)),
        ],
    }


class RedcodeLexer(RegexLexer):
    """
    A simple Redcode lexer based on ICWS'94.
    Contributed by Adam Blinkinsop <blinks@acm.org>.

    *New in Pygments 0.8.*
    """
    name = 'Redcode'
    aliases = ['redcode']
    filenames = ['*.cw']

    opcodes = ['DAT','MOV','ADD','SUB','MUL','DIV','MOD',
               'JMP','JMZ','JMN','DJN','CMP','SLT','SPL',
               'ORG','EQU','END']
    modifiers = ['A','B','AB','BA','F','X','I']

    tokens = {
        'root': [
            # Whitespace:
            (r'\s+', Text),
            (r';.*$', Comment.Single),
            # Lexemes:
            #  Identifiers
            (r'\b(%s)\b' % '|'.join(opcodes), Name.Function),
            (r'\b(%s)\b' % '|'.join(modifiers), Name.Decorator),
            (r'[A-Za-z_][A-Za-z_0-9]+', Name),
            #  Operators
            (r'[-+*/%]', Operator),
            (r'[#$@<>]', Operator), # mode
            (r'[.,]', Punctuation), # mode
            #  Numbers
            (r'[-+]?\d+', Number.Integer),
        ],
    }


class MOOCodeLexer(RegexLexer):
    """
    For `MOOCode <http://www.moo.mud.org/>`_ (the MOO scripting
    language).

    *New in Pygments 0.9.*
    """
    name = 'MOOCode'
    filenames = ['*.moo']
    aliases = ['moocode']
    mimetypes = ['text/x-moocode']

    tokens = {
        'root' : [
            # Numbers
            (r'(0|[1-9][0-9_]*)', Number.Integer),
            # Strings
            (r'"(\\\\|\\"|[^"])*"', String),
            # exceptions
            (r'(E_PERM|E_DIV)', Name.Exception),
            # db-refs
            (r'((#[-0-9]+)|(\$[a-z_A-Z0-9]+))', Name.Entity),
            # Keywords
            (r'\b(if|else|elseif|endif|for|endfor|fork|endfork|while'
             r'|endwhile|break|continue|return|try'
             r'|except|endtry|finally|in)\b', Keyword),
            # builtins
            (r'(random|length)', Name.Builtin),
            # special variables
            (r'(player|caller|this|args)', Name.Variable.Instance),
            # skip whitespace
            (r'\s+', Text),
            (r'\n', Text),
            # other operators
            (r'([!;=,{}&\|:\.\[\]@\(\)\<\>\?]+)', Operator),
            # function call
            (r'([a-z_A-Z0-9]+)(\()', bygroups(Name.Function, Operator)),
            # variables
            (r'([a-zA-Z_0-9]+)', Text),
        ]
    }

class SmalltalkLexer(RegexLexer):
    """
    For `Smalltalk <http://www.smalltalk.org/>`_ syntax.
    Contributed by Stefan Matthias Aust.

    *New in Pygments 0.10.*
    """
    name = 'Smalltalk'
    filenames = ['*.st']
    aliases = ['smalltalk', 'squeak']
    mimetypes = ['text/x-smalltalk']

    tokens = {
        'root' : [
            # Squeak fileout format (optional)
            (r'^"[^"]*"!', Keyword),
            (r"^'[^']*'!", Keyword),
            (r'^(!)(\w+)( commentStamp: )(.*?)( prior: .*?!\n)(.*?)(!)',
                bygroups(Keyword, Name.Class, Keyword, String, Keyword, Text, Keyword)),
            (r'^(!)(\w+(?: class)?)( methodsFor: )(\'[^\']*\')(.*?!)',
                bygroups(Keyword, Name.Class, Keyword, String, Keyword)),
            (r'^(\w+)( subclass: )(#\w+)'
             r'(\s+instanceVariableNames: )(.*?)'
             r'(\s+classVariableNames: )(.*?)'
             r'(\s+poolDictionaries: )(.*?)'
             r'(\s+category: )(.*?)(!)',
                bygroups(Name.Class, Keyword, String.Symbol, Keyword, String, Keyword,
                         String, Keyword, String, Keyword, String, Keyword)),
            (r'^(\w+(?: class)?)(\s+instanceVariableNames: )(.*?)(!)',
                bygroups(Name.Class, Keyword, String, Keyword)),
            (r'(!\n)(\].*)(! !)$', bygroups(Keyword, Text, Keyword)),
            (r'! !$', Keyword),
            # skip whitespace and comments
            (r'\s+', Text),
            (r'"[^"]*"', Comment),
            # method patterns
            (r'^(\w+)(\s*:\s*)(\w+\s*)', bygroups(Name.Function, Punctuation,
                                                  Name.Variable), 'pattern'),
            (r'^([-+*/\\~<>=|&!?,@%]+\s*)(\w+)', bygroups(Name.Function, Name.Variable)),
            (r'^(\w+)', Name.Function),
            # literals
            (r'\'[^\']*\'', String),
            (r'\$.', String.Char),
            (r'#\(', String.Symbol, 'parenth'),
            (r'(\d+r)?-?\d+(\.\d+)?(e-?\d+)?', Number),
            (r'#("[^"]*"|[-+*/\\~<>=|&!?,@%]+|[\w:]+)', String.Symbol),
            # blocks variables
            (r'(\[\s*)((?::\w+\s*)+)(\|)', bygroups(Text, Name.Variable, Text)),
            # temporaries
            (r'(\|)([\w\s]*)(\|)', bygroups(Operator, Name.Variable, Operator)),
            # names
            (r'\b(ifTrue:|ifFalse:|whileTrue:|whileFalse:|timesRepeat:)', Name.Builtin),
            (r'\b(self|super)\b', Name.Builtin.Pseudo),
            (r'\b[A-Z]\w*:', Name),
            (r'\b[A-Z]\w*\b', Name), #Name.Class),
            (r'\w+:?|[-+*/\\~<>=|&!?,@%]+', Name), #Name.Function),
            # syntax
            (r'\^|:=', Operator),
            (r'[\[\](){}.;]', Text),
        ],
        'parenth' : [
            (r'\)', String.Symbol, '#pop'),
            include('root'),
        ],
        'pattern' : [
            (r'(\w+)(\s*:\s*)(\w+\s*)', bygroups(Name.Function, Punctuation,
                                                 Name.Variable)),
            (r'', Text, '#pop'),
        ],
    }


class TcshLexer(RegexLexer):
    """
    Lexer for tcsh scripts.

    *New in Pygments 0.10.*
    """

    name = 'Tcsh'
    aliases = ['tcsh', 'csh']
    filenames = ['*.tcsh', '*.csh']
    mimetypes = ['application/x-csh']

    tokens = {
        'root': [
            include('basic'),
            (r'\$\(', Keyword, 'paren'),
            (r'\${#?', Keyword, 'curly'),
            (r'`', String.Backtick, 'backticks'),
            include('data'),
        ],
        'basic': [
            (r'\b(if|endif|else|while|then|foreach|case|default|'
             r'continue|goto|breaksw|end|switch|endsw)\s*\b',
             Keyword),
            (r'\b(alias|alloc|bg|bindkey|break|builtins|bye|caller|cd|chdir|'
             r'complete|dirs|echo|echotc|eval|exec|exit|'
             r'fg|filetest|getxvers|glob|getspath|hashstat|history|hup|inlib|jobs|kill|'
             r'limit|log|login|logout|ls-F|migrate|newgrp|nice|nohup|notify|'
             r'onintr|popd|printenv|pushd|rehash|repeat|rootnode|popd|pushd|set|shift|'
             r'sched|setenv|setpath|settc|setty|setxvers|shift|source|stop|suspend|'
             r'source|suspend|telltc|time|'
             r'umask|unalias|uncomplete|unhash|universe|unlimit|unset|unsetenv|'
             r'ver|wait|warp|watchlog|where|which)\s*\b',
             Name.Builtin),
            (r'#.*\n', Comment),
            (r'\\[\w\W]', String.Escape),
            (r'(\b\w+)(\s*)(=)', bygroups(Name.Variable, Text, Operator)),
            (r'[\[\]{}()=]+', Operator),
            (r'<<\s*(\'?)\\?(\w+)[\w\W]+?\2', String),
        ],
        'data': [
            (r'"(\\\\|\\[0-7]+|\\.|[^"])*"', String.Double),
            (r"'(\\\\|\\[0-7]+|\\.|[^'])*'", String.Single),
            (r'\s+', Text),
            (r'[^=\s\n\[\]{}()$"\'`\\]+', Text),
            (r'\d+(?= |\Z)', Number),
            (r'\$#?(\w+|.)', Name.Variable),
        ],
        'curly': [
            (r'}', Keyword, '#pop'),
            (r':-', Keyword),
            (r'[a-zA-Z0-9_]+', Name.Variable),
            (r'[^}:"\'`$]+', Punctuation),
            (r':', Punctuation),
            include('root'),
        ],
        'paren': [
            (r'\)', Keyword, '#pop'),
            include('root'),
        ],
        'backticks': [
            (r'`', String.Backtick, '#pop'),
            include('root'),
        ],
    }


class LogtalkLexer(RegexLexer):
    """
    For `Logtalk <http://logtalk.org/>`_ source code.

    *New in Pygments 0.10.*
    """

    name = 'Logtalk'
    aliases = ['logtalk']
    filenames = ['*.lgt']
    mimetypes = ['text/x-logtalk']

    tokens = {
        'root': [
            # Directives
            (r'^\s*:-\s',Punctuation,'directive'),
            # Comments
            (r'%.*?\n', Comment),
            (r'/\*(.|\n)*?\*/',Comment),
            # Whitespace
            (r'\n', Text),
            (r'\s+', Text),
            # Numbers
            (r"0'.", Number),
            (r'0b[01]+', Number),
            (r'0o[0-7]+', Number),
            (r'0x[0-9a-fA-F]+', Number),
            (r'\d+\.?\d*((e|E)(\+|-)?\d+)?', Number),
            # Variables
            (r'([A-Z_][a-zA-Z0-9_]*)', Name.Variable),
            # Event handlers
            (r'(after|before)(?=[(])', Keyword),
            # Execution-context methods
            (r'(parameter|this|se(lf|nder))(?=[(])', Keyword),
            # Reflection
            (r'(current_predicate|predicate_property)(?=[(])', Keyword),
            # DCGs and term expansion
            (r'(expand_term|(goal|term)_expansion|phrase)(?=[(])', Keyword),
            # Entity
            (r'(abolish|c(reate|urrent))_(object|protocol|category)(?=[(])',
             Keyword),
            (r'(object|protocol|category)_property(?=[(])', Keyword),
            # Entity relations
            (r'complements_object(?=[(])', Keyword),
            (r'extends_(object|protocol|category)(?=[(])', Keyword),
            (r'imp(lements_protocol|orts_category)(?=[(])', Keyword),
            (r'(instantiat|specializ)es_class(?=[(])', Keyword),
            # Events
            (r'(current_event|(abolish|define)_events)(?=[(])', Keyword),
            # Flags
            (r'(current|set)_logtalk_flag(?=[(])', Keyword),
            # Compiling, loading, and library paths
            (r'logtalk_(compile|l(ibrary_path|oad))(?=[(])', Keyword),
            # Database
            (r'(clause|retract(all)?)(?=[(])', Keyword),
            (r'a(bolish|ssert(a|z))(?=[(])', Keyword),
            # Control
            (r'(ca(ll|tch)|throw)(?=[(])', Keyword),
            (r'(fail|true)\b', Keyword),
            # All solutions
            (r'((bag|set)of|f(ind|or)all)(?=[(])', Keyword),
            # Multi-threading meta-predicates
            (r'threaded(_(call|once|ignore|exit|peek|wait|notify))?(?=[(])',
             Keyword),
            # Term unification
            (r'unify_with_occurs_check(?=[(])', Keyword),
            # Term creation and decomposition
            (r'(functor|arg|copy_term)(?=[(])', Keyword),
            # Evaluable functors
            (r'(rem|mod|abs|sign)(?=[(])', Keyword),
            (r'float(_(integer|fractional)_part)?(?=[(])', Keyword),
            (r'(floor|truncate|round|ceiling)(?=[(])', Keyword),
            # Other arithmetic functors
            (r'(cos|atan|exp|log|s(in|qrt))(?=[(])', Keyword),
            # Term testing
            (r'(var|atom(ic)?|integer|float|compound|n(onvar|umber))(?=[(])',
             Keyword),
            # Stream selection and control
            (r'(curren|se)t_(in|out)put(?=[(])', Keyword),
            (r'(open|close)(?=[(])', Keyword),
            (r'flush_output(?=[(])', Keyword),
            (r'(at_end_of_stream|flush_output)\b', Keyword),
            (r'(stream_property|at_end_of_stream|set_stream_position)(?=[(])',
             Keyword),
            # Character and byte input/output
            (r'(nl|(get|peek|put)_(byte|c(har|ode)))(?=[(])', Keyword),
            (r'\bnl\b', Keyword),
            # Term input/output
            (r'read(_term)?(?=[(])', Keyword),
            (r'write(q|_(canonical|term))?(?=[(])', Keyword),
            (r'(current_)?op(?=[(])', Keyword),
            (r'(current_)?char_conversion(?=[(])', Keyword),
            # Atomic term processing
            (r'atom_(length|c(hars|o(ncat|des)))(?=[(])', Keyword),
            (r'(char_code|sub_atom)(?=[(])', Keyword),
            (r'number_c(har|ode)s(?=[(])', Keyword),
            # Implementation defined hooks functions
            (r'(se|curren)t_prolog_flag(?=[(])', Keyword),
            (r'\bhalt\b', Keyword),
            (r'halt(?=[(])', Keyword),
            # Message sending operators
            (r'(::|:|\^\^)', Operator),
            # External call
            (r'[{}]', Keyword),
            # Logic and control
            (r'\bonce(?=[(])', Keyword),
            (r'\brepeat\b', Keyword),
            # Bitwise functors
            (r'(>>|<<|/\\|\\\\|\\)', Operator),
            # Arithemtic evaluation
            (r'\bis\b', Keyword),
            # Arithemtic comparison
            (r'(=:=|=\\=|<|=<|>=|>)', Operator),
            # Term creation and decomposition
            (r'=\.\.', Operator),
            # Term unification
            (r'(=|\\=)', Operator),
            # Term comparison
            (r'(==|\\==|@=<|@<|@>=|@>)', Operator),
            # Evaluable functors
            (r'(//|[-+*/])', Operator),
            (r'\b(mod|rem)\b', Operator),
            # Other arithemtic functors
            (r'\b\*\*\b', Operator),
            # DCG rules
            (r'-->', Operator),
            # Control constructs
            (r'([!;]|->)', Operator),
            # Logic and control
            (r'\\+', Operator),
            # Mode operators
            (r'[?@]', Operator),
            # Strings
            (r'"(\\\\|\\"|[^"])*"', String),
            # Ponctuation
            (r'[()\[\],.|]', Text),
            # Atoms
            (r"[a-z][a-zA-Z0-9_]*", Text),
            (r"[']", String, 'quoted_atom'),
        ],

        'quoted_atom': [
            (r"['][']", String),
            (r"[']", String, '#pop'),
            (r'\\([\\abfnrtv"\']|(x[a-fA-F0-9]+|[0-7]+)\\)', String.Escape),
            (r"[^\\'\n]+", String),
            (r'\\', String),
        ],

        'directive': [
            # Entity directives
            (r'(category|object|protocol)(?=[(])', Keyword, 'entityrelations'),
            (r'(end_(category|object|protocol))[.]',Keyword, 'root'),
            # Predicate scope directives
            (r'(public|protected|private)(?=[(])', Keyword, 'root'),
            # Other directives
            (r'e(ncoding|xport)(?=[(])', Keyword, 'root'),
            (r'in(fo|itialization)(?=[(])', Keyword, 'root'),
            (r'(dynamic|synchronized|threaded)[.]', Keyword, 'root'),
            (r'(alias|d(ynamic|iscontiguous)|m(eta_predicate|ode|ultifile)'
             r'|synchronized)(?=[(])', Keyword, 'root'),
            (r'op(?=[(])', Keyword, 'root'),
            (r'(calls|use(s|_module))(?=[(])', Keyword, 'root'),
            (r'[a-z][a-zA-Z0-9_]*(?=[(])', Text, 'root'),
            (r'[a-z][a-zA-Z0-9_]*[.]', Text, 'root'),
        ],

        'entityrelations': [
            (r'(extends|i(nstantiates|mp(lements|orts))|specializes)(?=[(])',
             Keyword),
            # Numbers
            (r"0'.", Number),
            (r'0b[01]+', Number),
            (r'0o[0-7]+', Number),
            (r'0x[0-9a-fA-F]+', Number),
            (r'\d+\.?\d*((e|E)(\+|-)?\d+)?', Number),
            # Variables
            (r'([A-Z_][a-zA-Z0-9_]*)', Name.Variable),
            # Atoms
            (r"[a-z][a-zA-Z0-9_]*", Text),
            (r"[']", String, 'quoted_atom'),
            # Strings
            (r'"(\\\\|\\"|[^"])*"', String),
            # End of entity-opening directive
            (r'([)]\.)', Text, 'root'),
            # Scope operator
            (r'(::)', Operator),
            # Ponctuation
            (r'[()\[\],.|]', Text),
            # Comments
            (r'%.*?\n', Comment),
            (r'/\*(.|\n)*?\*/',Comment),
            # Whitespace
            (r'\n', Text),
            (r'\s+', Text),
        ]
    }


def _shortened(word):
    dpos = word.find('$')
    return '|'.join([word[:dpos] + word[dpos+1:i] + r'\b'
                     for i in range(len(word), dpos, -1)])
def _shortened_many(*words):
    return '|'.join(map(_shortened, words))

class GnuplotLexer(RegexLexer):
    """
    For `Gnuplot <http://gnuplot.info/>`_ plotting scripts.

    *New in Pygments 0.11.*
    """

    name = 'Gnuplot'
    aliases = ['gnuplot']
    filenames = ['*.plot', '*.plt']
    mimetypes = ['text/x-gnuplot']

    tokens = {
        'root': [
            include('whitespace'),
            (_shortened('bi$nd'), Keyword, 'bind'),
            (_shortened_many('ex$it', 'q$uit'), Keyword, 'quit'),
            (_shortened('f$it'), Keyword, 'fit'),
            (r'(if)(\s*)(\()', bygroups(Keyword, Text, Punctuation), 'if'),
            (r'else\b', Keyword),
            (_shortened('pa$use'), Keyword, 'pause'),
            (_shortened_many('p$lot', 'rep$lot', 'sp$lot'), Keyword, 'plot'),
            (_shortened('sa$ve'), Keyword, 'save'),
            (_shortened('se$t'), Keyword, ('genericargs', 'optionarg')),
            (_shortened_many('sh$ow', 'uns$et'),
             Keyword, ('noargs', 'optionarg')),
            (_shortened_many('low$er', 'ra$ise', 'ca$ll', 'cd$', 'cl$ear',
                             'h$elp', '\\?$', 'hi$story', 'l$oad', 'pr$int',
                             'pwd$', 're$read', 'res$et', 'scr$eendump',
                             'she$ll', 'sy$stem', 'up$date'),
             Keyword, 'genericargs'),
            (_shortened_many('pwd$', 're$read', 'res$et', 'scr$eendump',
                             'she$ll', 'test$'),
             Keyword, 'noargs'),
            ('([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(=)',
             bygroups(Name.Variable, Text, Operator), 'genericargs'),
            ('([a-zA-Z_][a-zA-Z0-9_]*)(\s*\(.*?\)\s*)(=)',
             bygroups(Name.Function, Text, Operator), 'genericargs'),
            (r'@[a-zA-Z_][a-zA-Z0-9_]*', Name.Constant), # macros
            (r';', Keyword),
        ],
        'comment': [
            (r'[^\\\n]', Comment),
            (r'\\\n', Comment),
            (r'\\', Comment),
            # don't add the newline to the Comment token
            ('', Comment, '#pop'),
        ],
        'whitespace': [
            ('#', Comment, 'comment'),
            (r'[ \t\v\f]+', Text),
        ],
        'noargs': [
            include('whitespace'),
            # semicolon and newline end the argument list
            (r';', Punctuation, '#pop'),
            (r'\n', Text, '#pop'),
        ],
        'dqstring': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String), # all other characters
            (r'\\\n', String), # line continuation
            (r'\\', String), # stray backslash
            (r'\n', String, '#pop'), # newline ends the string too
        ],
        'sqstring': [
            (r"''", String), # escaped single quote
            (r"'", String, '#pop'),
            (r"[^\\'\n]+", String), # all other characters
            (r'\\\n', String), # line continuation
            (r'\\', String), # normal backslash
            (r'\n', String, '#pop'), # newline ends the string too
        ],
        'genericargs': [
            include('noargs'),
            (r'"', String, 'dqstring'),
            (r"'", String, 'sqstring'),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+', Number.Float),
            (r'(\d+\.\d*|\.\d+)', Number.Float),
            (r'-?\d+', Number.Integer),
            ('[,.~!%^&*+=|?:<>/-]', Operator),
            ('[{}()\[\]]', Punctuation),
            (r'(eq|ne)\b', Operator.Word),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)(\s*)(\()',
             bygroups(Name.Function, Text, Punctuation)),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
            (r'@[a-zA-Z_][a-zA-Z0-9_]*', Name.Constant), # macros
            (r'\\\n', Text),
        ],
        'optionarg': [
            include('whitespace'),
            (_shortened_many(
                "a$ll","an$gles","ar$row","au$toscale","b$ars","bor$der",
                "box$width","cl$abel","c$lip","cn$trparam","co$ntour","da$ta",
                "data$file","dg$rid3d","du$mmy","enc$oding","dec$imalsign",
                "fit$","font$path","fo$rmat","fu$nction","fu$nctions","g$rid",
                "hid$den3d","his$torysize","is$osamples","k$ey","keyt$itle",
                "la$bel","li$nestyle","ls$","loa$dpath","loc$ale","log$scale",
                "mac$ros","map$ping","map$ping3d","mar$gin","lmar$gin",
                "rmar$gin","tmar$gin","bmar$gin","mo$use","multi$plot",
                "mxt$ics","nomxt$ics","mx2t$ics","nomx2t$ics","myt$ics",
                "nomyt$ics","my2t$ics","nomy2t$ics","mzt$ics","nomzt$ics",
                "mcbt$ics","nomcbt$ics","of$fsets","or$igin","o$utput",
                "pa$rametric","pm$3d","pal$ette","colorb$ox","p$lot",
                "poi$ntsize","pol$ar","pr$int","obj$ect","sa$mples","si$ze",
                "st$yle","su$rface","table$","t$erminal","termo$ptions","ti$cs",
                "ticsc$ale","ticsl$evel","timef$mt","tim$estamp","tit$le",
                "v$ariables","ve$rsion","vi$ew","xyp$lane","xda$ta","x2da$ta",
                "yda$ta","y2da$ta","zda$ta","cbda$ta","xl$abel","x2l$abel",
                "yl$abel","y2l$abel","zl$abel","cbl$abel","xti$cs","noxti$cs",
                "x2ti$cs","nox2ti$cs","yti$cs","noyti$cs","y2ti$cs","noy2ti$cs",
                "zti$cs","nozti$cs","cbti$cs","nocbti$cs","xdti$cs","noxdti$cs",
                "x2dti$cs","nox2dti$cs","ydti$cs","noydti$cs","y2dti$cs",
                "noy2dti$cs","zdti$cs","nozdti$cs","cbdti$cs","nocbdti$cs",
                "xmti$cs","noxmti$cs","x2mti$cs","nox2mti$cs","ymti$cs",
                "noymti$cs","y2mti$cs","noy2mti$cs","zmti$cs","nozmti$cs",
                "cbmti$cs","nocbmti$cs","xr$ange","x2r$ange","yr$ange",
                "y2r$ange","zr$ange","cbr$ange","rr$ange","tr$ange","ur$ange",
                "vr$ange","xzeroa$xis","x2zeroa$xis","yzeroa$xis","y2zeroa$xis",
                "zzeroa$xis","zeroa$xis","z$ero"), Name.Builtin, '#pop'),
        ],
        'bind': [
            ('!', Keyword, '#pop'),
            (_shortened('all$windows'), Name.Builtin),
            include('genericargs'),
        ],
        'quit': [
            (r'gnuplot\b', Keyword),
            include('noargs'),
        ],
        'fit': [
            (r'via\b', Name.Builtin),
            include('plot'),
        ],
        'if': [
            (r'\)', Punctuation, '#pop'),
            include('genericargs'),
        ],
        'pause': [
            (r'(mouse|any|button1|button2|button3)\b', Name.Builtin),
            (_shortened('key$press'), Name.Builtin),
            include('genericargs'),
        ],
        'plot': [
            (_shortened_many('ax$es', 'axi$s', 'bin$ary', 'ev$ery', 'i$ndex',
                             'mat$rix', 's$mooth', 'thru$', 't$itle',
                             'not$itle', 'u$sing', 'w$ith'),
             Name.Builtin),
            include('genericargs'),
        ],
        'save': [
            (_shortened_many('f$unctions', 's$et', 't$erminal', 'v$ariables'),
             Name.Builtin),
            include('genericargs'),
        ],
    }


class PovrayLexer(RegexLexer):
    """
    For `Persistence of Vision Raytracer http://www.povray.org/>`_ files.

    *New in Pygments 0.11.*
    """
    name = 'POVRay'
    aliases = ['pov']
    filenames = ['*.pov', '*.inc']
    mimetypes = ['text/x-povray']

    tokens = {
        'root': [
            (r'/\*[\w\W]*?\*/', Comment.Multiline),
            (r'//.*\n', Comment.Single),
            (r'"(?:\\.|[^"])+"', String.Double),
            (r'#(debug|default|else|end|error|fclose|fopen|if|ifdef|ifndef|'
             r'include|range|read|render|statistics|switch|undef|version|'
             r'warning|while|write|define|macro|local|declare)',
             Comment.Preproc),
            (r'\b(aa_level|aa_threshold|abs|acos|acosh|adaptive|adc_bailout|'
             r'agate|agate_turb|all|alpha|ambient|ambient_light|angle|'
             r'aperture|arc_angle|area_light|asc|asin|asinh|assumed_gamma|'
             r'atan|atan2|atanh|atmosphere|atmospheric_attenuation|'
             r'attenuating|average|background|black_hole|blue|blur_samples|'
             r'bounded_by|box_mapping|bozo|break|brick|brick_size|'
             r'brightness|brilliance|bumps|bumpy1|bumpy2|bumpy3|bump_map|'
             r'bump_size|case|caustics|ceil|checker|chr|clipped_by|clock|'
             r'color|color_map|colour|colour_map|component|composite|concat|'
             r'confidence|conic_sweep|constant|control0|control1|cos|cosh|'
             r'count|crackle|crand|cube|cubic_spline|cylindrical_mapping|'
             r'debug|declare|default|degrees|dents|diffuse|direction|'
             r'distance|distance_maximum|div|dust|dust_type|eccentricity|'
             r'else|emitting|end|error|error_bound|exp|exponent|'
             r'fade_distance|fade_power|falloff|falloff_angle|false|'
             r'file_exists|filter|finish|fisheye|flatness|flip|floor|'
             r'focal_point|fog|fog_alt|fog_offset|fog_type|frequency|gif|'
             r'global_settings|glowing|gradient|granite|gray_threshold|'
             r'green|halo|hexagon|hf_gray_16|hierarchy|hollow|hypercomplex|'
             r'if|ifdef|iff|image_map|incidence|include|int|interpolate|'
             r'inverse|ior|irid|irid_wavelength|jitter|lambda|leopard|'
             r'linear|linear_spline|linear_sweep|location|log|looks_like|'
             r'look_at|low_error_factor|mandel|map_type|marble|material_map|'
             r'matrix|max|max_intersections|max_iteration|max_trace_level|'
             r'max_value|metallic|min|minimum_reuse|mod|mortar|'
             r'nearest_count|no|normal|normal_map|no_shadow|number_of_waves|'
             r'octaves|off|offset|omega|omnimax|on|once|onion|open|'
             r'orthographic|panoramic|pattern1|pattern2|pattern3|'
             r'perspective|pgm|phase|phong|phong_size|pi|pigment|'
             r'pigment_map|planar_mapping|png|point_at|pot|pow|ppm|'
             r'precision|pwr|quadratic_spline|quaternion|quick_color|'
             r'quick_colour|quilted|radial|radians|radiosity|radius|rainbow|'
             r'ramp_wave|rand|range|reciprocal|recursion_limit|red|'
             r'reflection|refraction|render|repeat|rgb|rgbf|rgbft|rgbt|'
             r'right|ripples|rotate|roughness|samples|scale|scallop_wave|'
             r'scattering|seed|shadowless|sin|sine_wave|sinh|sky|sky_sphere|'
             r'slice|slope_map|smooth|specular|spherical_mapping|spiral|'
             r'spiral1|spiral2|spotlight|spotted|sqr|sqrt|statistics|str|'
             r'strcmp|strength|strlen|strlwr|strupr|sturm|substr|switch|sys|'
             r't|tan|tanh|test_camera_1|test_camera_2|test_camera_3|'
             r'test_camera_4|texture|texture_map|tga|thickness|threshold|'
             r'tightness|tile2|tiles|track|transform|translate|transmit|'
             r'triangle_wave|true|ttf|turbulence|turb_depth|type|'
             r'ultra_wide_angle|up|use_color|use_colour|use_index|u_steps|'
             r'val|variance|vaxis_rotate|vcross|vdot|version|vlength|'
             r'vnormalize|volume_object|volume_rendered|vol_with_light|'
             r'vrotate|v_steps|warning|warp|water_level|waves|while|width|'
             r'wood|wrinkles|yes)\b', Keyword),
            (r'bicubic_patch|blob|box|camera|cone|cubic|cylinder|difference|'
             r'disc|height_field|intersection|julia_fractal|lathe|'
             r'light_source|merge|mesh|object|plane|poly|polygon|prism|'
             r'quadric|quartic|smooth_triangle|sor|sphere|superellipsoid|'
             r'text|torus|triangle|union', Name.Builtin),
            #TODO: <=, etc
            (r'[\[\](){}<>;,]', Punctuation),
            (r'[-+*/=]', Operator),
            (r'\b(x|y|z|u|v)\b', Name.Builtin.Pseudo),
            (r'[a-zA-Z_][a-zA-Z_0-9]*', Name),
            (r'[0-9]+\.[0-9]*', Number.Float),
            (r'\.[0-9]+', Number.Float),
            (r'[0-9]+', Number.Integer),
            (r'\s+', Text),
        ]
    }
