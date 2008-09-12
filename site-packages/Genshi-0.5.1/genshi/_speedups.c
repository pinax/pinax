/*
 * Copyright (C) 2006-2008 Edgewall Software
 * All rights reserved.
 *
 * This software is licensed as described in the file COPYING, which
 * you should have received as part of this distribution. The terms
 * are also available at http://genshi.edgewall.org/wiki/License.
 *
 * This software consists of voluntary contributions made by many
 * individuals. For the exact contribution history, see the revision
 * history and logs, available at http://genshi.edgewall.org/log/.
 */

#include <Python.h>
#include <structmember.h>

#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif

static PyObject *amp1, *amp2, *lt1, *lt2, *gt1, *gt2, *qt1, *qt2;
static PyObject *stripentities, *striptags;

static void
init_constants(void)
{
    PyObject *util = PyImport_ImportModule("genshi.util");
    stripentities = PyObject_GetAttrString(util, "stripentities");
    striptags = PyObject_GetAttrString(util, "striptags");
    Py_DECREF(util);

    amp1 = PyUnicode_DecodeASCII("&", 1, NULL);
    amp2 = PyUnicode_DecodeASCII("&amp;", 5, NULL);
    lt1 = PyUnicode_DecodeASCII("<", 1, NULL);
    lt2 = PyUnicode_DecodeASCII("&lt;", 4, NULL);
    gt1 = PyUnicode_DecodeASCII(">", 1, NULL);
    gt2 = PyUnicode_DecodeASCII("&gt;", 4, NULL);
    qt1 = PyUnicode_DecodeASCII("\"", 1, NULL);
    qt2 = PyUnicode_DecodeASCII("&#34;", 5, NULL);
}

/* Markup class */

PyAPI_DATA(PyTypeObject) MarkupType;

PyDoc_STRVAR(Markup__doc__,
"Marks a string as being safe for inclusion in HTML/XML output without\n\
needing to be escaped.");

static PyObject *
escape(PyObject *text, int quotes)
{
    PyObject *args, *ret;
    PyUnicodeObject *in, *out;
    Py_UNICODE *inp, *outp;
    int len, inn, outn;

    if (PyObject_TypeCheck(text, &MarkupType)) {
        Py_INCREF(text);
        return text;
    }
    if (PyObject_HasAttrString(text, "__html__")) {
        ret = PyObject_CallMethod(text, "__html__", NULL);
        args = PyTuple_New(1);
        if (args == NULL) {
            Py_DECREF(ret);
            return NULL;
        }
        PyTuple_SET_ITEM(args, 0, ret);
        ret = MarkupType.tp_new(&MarkupType, args, NULL);
        Py_DECREF(args);
        return ret;
    }
    in = (PyUnicodeObject *) PyObject_Unicode(text);
    if (in == NULL) {
        return NULL;
    }
    /* First we need to figure out how long the escaped string will be */
    len = inn = 0;
    inp = in->str;
    while (*(inp) || in->length > inp - in->str) {
        switch (*inp++) {
            case '&': len += 5; inn++;                                 break;
            case '"': len += quotes ? 5 : 1; inn += quotes ? 1 : 0;    break;
            case '<':
            case '>': len += 4; inn++;                                 break;
            default:  len++;
        }
    }

    /* Do we need to escape anything at all? */
    if (!inn) {
        args = PyTuple_New(1);
        if (args == NULL) {
            Py_DECREF((PyObject *) in);
            return NULL;
        }
        PyTuple_SET_ITEM(args, 0, (PyObject *) in);
        ret = MarkupType.tp_new(&MarkupType, args, NULL);
        Py_DECREF(args);
        return ret;
    }

    out = (PyUnicodeObject*) PyUnicode_FromUnicode(NULL, len);
    if (out == NULL) {
        Py_DECREF((PyObject *) in);
        return NULL;
    }

    outn = 0;
    inp = in->str;
    outp = out->str;
    while (*(inp) || in->length > inp - in->str) {
        if (outn == inn) {
            /* copy rest of string if we have already replaced everything */
            Py_UNICODE_COPY(outp, inp, in->length - (inp - in->str));
            break;
        }
        switch (*inp) {
            case '&':
                Py_UNICODE_COPY(outp, ((PyUnicodeObject *) amp2)->str, 5);
                outp += 5;
                outn++;
                break;
            case '"':
                if (quotes) {
                    Py_UNICODE_COPY(outp, ((PyUnicodeObject *) qt2)->str, 5);
                    outp += 5;
                    outn++;
                } else {
                    *outp++ = *inp;
                }
                break;
            case '<':
                Py_UNICODE_COPY(outp, ((PyUnicodeObject *) lt2)->str, 4);
                outp += 4;
                outn++;
                break;
            case '>':
                Py_UNICODE_COPY(outp, ((PyUnicodeObject *) gt2)->str, 4);
                outp += 4;
                outn++;
                break;
            default:
                *outp++ = *inp;
        }
        inp++;
    }

    Py_DECREF((PyObject *) in);

    args = PyTuple_New(1);
    if (args == NULL) {
        Py_DECREF((PyObject *) out);
        return NULL;
    }
    PyTuple_SET_ITEM(args, 0, (PyObject *) out);
    ret = MarkupType.tp_new(&MarkupType, args, NULL);
    Py_DECREF(args);
    return ret;
}

PyDoc_STRVAR(escape__doc__,
"Create a Markup instance from a string and escape special characters\n\
it may contain (<, >, & and \").\n\
\n\
>>> escape('\"1 < 2\"')\n\
<Markup u'&#34;1 &lt; 2&#34;'>\n\
\n\
If the `quotes` parameter is set to `False`, the \" character is left\n\
as is. Escaping quotes is generally only required for strings that are\n\
to be used in attribute values.\n\
\n\
>>> escape('\"1 < 2\"', quotes=False)\n\
<Markup u'\"1 &lt; 2\"'>\n\
\n\
:param text: the text to escape\n\
:param quotes: if ``True``, double quote characters are escaped in\n\
               addition to the other special characters\n\
:return: the escaped `Markup` string\n\
:rtype: `Markup`\n\
");

static PyObject *
Markup_escape(PyTypeObject* type, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"text", "quotes", 0};
    PyObject *text = NULL;
    char quotes = 1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|b", kwlist, &text, &quotes)) {
        return NULL;
    }
    if (PyObject_Not(text)) {
        return type->tp_new(type, args, NULL);
    }
    if (PyObject_TypeCheck(text, type)) {
        Py_INCREF(text);
        return text;
    }
    return escape(text, quotes);
}

static PyObject *
Markup_html(PyObject *self)
{
    Py_INCREF(self);
    return self;
}

PyDoc_STRVAR(join__doc__,
"Return a `Markup` object which is the concatenation of the strings\n\
in the given sequence, where this `Markup` object is the separator\n\
between the joined elements.\n\
\n\
Any element in the sequence that is not a `Markup` instance is\n\
automatically escaped.\n\
\n\
:param seq: the sequence of strings to join\n\
:param escape_quotes: whether double quote characters in the elements\n\
                      should be escaped\n\
:return: the joined `Markup` object\n\
:rtype: `Markup`\n\
:see: `escape`\n\
");

static PyObject *
Markup_join(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"seq", "escape_quotes", 0};
    PyObject *seq = NULL, *seq2, *tmp, *tmp2;
    char quotes = 1;
    int n, i;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|b", kwlist, &seq, &quotes)) {
        return NULL;
    }
    if (!PySequence_Check(seq)) {
        return NULL;
    }
    n = PySequence_Size(seq);
    if (n < 0) {
        return NULL;
    }
    seq2 = PyTuple_New(n);
    if (seq2 == NULL) {
        return NULL;
    }
    for (i = 0; i < n; i++) {
        tmp = PySequence_GetItem(seq, i);
        if (tmp == NULL) {
            Py_DECREF(seq2);
            return NULL;
        }
        tmp2 = escape(tmp, quotes);
        if (tmp2 == NULL) {
            Py_DECREF(seq2);
            return NULL;
        }
        PyTuple_SET_ITEM(seq2, i, tmp2);
        Py_DECREF(tmp);
    }
    tmp = PyUnicode_Join(self, seq2);
    Py_DECREF(seq2);
    if (tmp == NULL)
        return NULL;
    args = PyTuple_New(1);
    if (args == NULL) {
        Py_DECREF(tmp);
        return NULL;
    }
    PyTuple_SET_ITEM(args, 0, tmp);
    tmp = MarkupType.tp_new(&MarkupType, args, NULL);
    Py_DECREF(args);
    return tmp;
}

static PyObject *
Markup_add(PyObject *self, PyObject *other)
{
    PyObject *tmp, *tmp2, *args, *ret;
    if (PyObject_TypeCheck(self, &MarkupType)) {
        tmp = escape(other, 1);
        if (tmp == NULL)
            return NULL;
        tmp2 = PyUnicode_Concat(self, tmp);
    } else { // __radd__
        tmp = escape(self, 1);
        if (tmp == NULL)
            return NULL;
        tmp2 = PyUnicode_Concat(tmp, other);
    }
    Py_DECREF(tmp);
    if (tmp2 == NULL)
        return NULL;
    args = PyTuple_New(1);
    if (args == NULL) {
        Py_DECREF(tmp2);
        return NULL;
    }
    PyTuple_SET_ITEM(args, 0, tmp2);
    ret = MarkupType.tp_new(&MarkupType, args, NULL);
    Py_DECREF(args);
    return ret;
}

static PyObject *
Markup_mod(PyObject *self, PyObject *args)
{
    PyObject *tmp, *tmp2, *ret, *args2;
    int i, nargs = 0;
    PyObject *kwds = NULL;

    if (PyDict_Check(args)) {
        kwds = args;
    }
    if (kwds && PyDict_Size(kwds)) {
        PyObject *kwcopy, *key, *value;
        Py_ssize_t pos = 0;

        kwcopy = PyDict_Copy( kwds );
        if (kwcopy == NULL) {
            return NULL;
        }
        while (PyDict_Next(kwcopy, &pos, &key, &value)) {
            tmp = escape(value, 1);
            if (tmp == NULL) {
                Py_DECREF(kwcopy);
                return NULL;
            }
            if (PyDict_SetItem(kwcopy, key, tmp) < 0) {
                Py_DECREF(tmp);
                Py_DECREF(kwcopy);
                return NULL;
            }
        }
        tmp = PyUnicode_Format(self, kwcopy);
        Py_DECREF(kwcopy);
        if (tmp == NULL) {
            return NULL;
        }
    } else if (PyTuple_Check(args)) {
        nargs = PyTuple_GET_SIZE(args);
        args2 = PyTuple_New(nargs);
        if (args2 == NULL) {
            return NULL;
        }
        for (i = 0; i < nargs; i++) {
            tmp = escape(PyTuple_GET_ITEM(args, i), 1);
            if (tmp == NULL) {
                Py_DECREF(args2);
                return NULL;
            }
            PyTuple_SET_ITEM(args2, i, tmp);
        }
        tmp = PyUnicode_Format(self, args2);
        Py_DECREF(args2);
        if (tmp == NULL) {
            return NULL;
        }
    } else {
        tmp2 = escape(args, 1);
        if (tmp2 == NULL) {
            return NULL;
        }
        tmp = PyUnicode_Format(self, tmp2);
        Py_DECREF(tmp2);
        if (tmp == NULL) {
            return NULL;
        }
    }
    args = PyTuple_New(1);
    if (args == NULL) {
        Py_DECREF(tmp);
        return NULL;
    }
    PyTuple_SET_ITEM(args, 0, tmp);
    ret = PyUnicode_Type.tp_new(&MarkupType, args, NULL);
    Py_DECREF(args);
    return ret;
}

static PyObject *
Markup_mul(PyObject *self, PyObject *num)
{
    PyObject *unicode, *result, *args;

    if (PyObject_TypeCheck(self, &MarkupType)) {
        unicode = PyObject_Unicode(self);
        if (unicode == NULL) return NULL;
        result = PyNumber_Multiply(unicode, num);
    } else { // __rmul__
        unicode = PyObject_Unicode(num);
        if (unicode == NULL) return NULL;
        result = PyNumber_Multiply(unicode, self);
    }
    Py_DECREF(unicode);

    if (result == NULL) return NULL;
    args = PyTuple_New(1);
    if (args == NULL) {
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(args, 0, result);
    result = PyUnicode_Type.tp_new(&MarkupType, args, NULL);
    Py_DECREF(args);

    return result;
}

static PyObject *
Markup_repr(PyObject *self)
{
    PyObject *format, *result, *args;

    format = PyString_FromString("<Markup %r>");
    if (format == NULL) return NULL;
    result = PyObject_Unicode(self);
    if (result == NULL) {
        Py_DECREF(format);
        return NULL;
    }
    args = PyTuple_New(1);
    if (args == NULL) {
        Py_DECREF(format);
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(args, 0, result);
    result = PyString_Format(format, args);
    Py_DECREF(format);
    Py_DECREF(args);
    return result;
}

PyDoc_STRVAR(unescape__doc__,
"Reverse-escapes &, <, >, and \" and returns a `unicode` object.\n\
\n\
>>> Markup('1 &lt; 2').unescape()\n\
u'1 < 2'\n\
\n\
:return: the unescaped string\n\
:rtype: `unicode`\n\
:see: `genshi.core.unescape`\n\
");

static PyObject *
Markup_unescape(PyObject* self)
{
    PyObject *tmp, *tmp2;

    tmp = PyUnicode_Replace(self, qt2, qt1, -1);
    if (tmp == NULL) return NULL;
    tmp2 = PyUnicode_Replace(tmp, gt2, gt1, -1);
    Py_DECREF(tmp);
    if (tmp2 == NULL) return NULL;
    tmp = PyUnicode_Replace(tmp2, lt2, lt1, -1);
    Py_DECREF(tmp2);
    if (tmp == NULL) return NULL;
    tmp2 = PyUnicode_Replace(tmp, amp2, amp1, -1);
    Py_DECREF(tmp);
    return tmp2;
}

PyDoc_STRVAR(stripentities__doc__,
"Return a copy of the text with any character or numeric entities\n\
replaced by the equivalent UTF-8 characters.\n\
\n\
If the `keepxmlentities` parameter is provided and evaluates to `True`,\n\
the core XML entities (``&amp;``, ``&apos;``, ``&gt;``, ``&lt;`` and\n\
``&quot;``) are not stripped.\n\
\n\
:return: a `Markup` instance with entities removed\n\
:rtype: `Markup`\n\
:see: `genshi.util.stripentities`\n\
");

static PyObject *
Markup_stripentities(PyObject* self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"keepxmlentities", 0};
    PyObject *result, *args2;
    char keepxml = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|b", kwlist, &keepxml)) {
        return NULL;
    }

    if (stripentities == NULL) return NULL;
    result = PyObject_CallFunction(stripentities, "Ob", self, keepxml);
    if (result == NULL) return NULL;
    args2 = PyTuple_New(1);
    if (args2 == NULL) {
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(args2, 0, result);
    result = MarkupType.tp_new(&MarkupType, args2, NULL);
    Py_DECREF(args2);
    return result;
}

PyDoc_STRVAR(striptags__doc__,
"""Return a copy of the text with all XML/HTML tags removed.\n\
\n\
:return: a `Markup` instance with all tags removed\n\
:rtype: `Markup`\n\
:see: `genshi.util.striptags`\n\
");

static PyObject *
Markup_striptags(PyObject* self)
{
    PyObject *result, *args;

    if (striptags == NULL) return NULL;
    result = PyObject_CallFunction(striptags, "O", self);
    if (result == NULL) return NULL;
    args = PyTuple_New(1);
    if (args == NULL) {
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(args, 0, result);
    result = MarkupType.tp_new(&MarkupType, args, NULL);
    Py_DECREF(args);
    return result;
}

typedef struct {
    PyUnicodeObject HEAD;
} MarkupObject;

static PyMethodDef Markup_methods[] = {
    {"__html__", (PyCFunction) Markup_html, METH_NOARGS, NULL},
    {"escape", (PyCFunction) Markup_escape,
     METH_VARARGS|METH_CLASS|METH_KEYWORDS, escape__doc__},
    {"join", (PyCFunction)Markup_join, METH_VARARGS|METH_KEYWORDS, join__doc__},
    {"unescape", (PyCFunction)Markup_unescape, METH_NOARGS, unescape__doc__},
    {"stripentities", (PyCFunction) Markup_stripentities,
     METH_VARARGS|METH_KEYWORDS, stripentities__doc__},
    {"striptags", (PyCFunction) Markup_striptags, METH_NOARGS,
     striptags__doc__},
    {NULL}  /* Sentinel */
};

static PyNumberMethods Markup_as_number = {
    Markup_add, /*nb_add*/
    0, /*nb_subtract*/
    Markup_mul, /*nb_multiply*/
    0, /*nb_divide*/
    Markup_mod, /*nb_remainder*/
};

PyTypeObject MarkupType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "genshi._speedups.Markup",
    sizeof(MarkupObject),
    0,
    0,          /*tp_dealloc*/
    0,          /*tp_print*/
    0,          /*tp_getattr*/
    0,          /*tp_setattr*/
    0,          /*tp_compare*/
    Markup_repr, /*tp_repr*/
    &Markup_as_number, /*tp_as_number*/
    0,          /*tp_as_sequence*/
    0,          /*tp_as_mapping*/
    0,          /*tp_hash */

    0,          /*tp_call*/
    0,          /*tp_str*/
    0,          /*tp_getattro*/
    0,          /*tp_setattro*/
    0,          /*tp_as_buffer*/

    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
    Markup__doc__,/*tp_doc*/

    0,          /*tp_traverse*/
    0,          /*tp_clear*/

    0,          /*tp_richcompare*/
    0,          /*tp_weaklistoffset*/

    0,          /*tp_iter*/
    0,          /*tp_iternext*/

    /* Attribute descriptor and subclassing stuff */

    Markup_methods,/*tp_methods*/
    0,          /*tp_members*/
    0,          /*tp_getset*/
    0,          /*tp_base*/
    0,          /*tp_dict*/

    0,          /*tp_descr_get*/
    0,          /*tp_descr_set*/
    0,          /*tp_dictoffset*/

    0,          /*tp_init*/
    0,          /*tp_alloc  will be set to PyType_GenericAlloc in module init*/
    0,          /*tp_new*/
    0,          /*tp_free  Low-level free-memory routine */
    0,          /*tp_is_gc For PyObject_IS_GC */
    0,          /*tp_bases*/
    0,          /*tp_mro method resolution order */
    0,          /*tp_cache*/
    0,          /*tp_subclasses*/
    0           /*tp_weaklist*/
};

PyMODINIT_FUNC
init_speedups(void)
{
    PyObject *module;

    /* Workaround for quirk in Visual Studio, see
        <http://www.python.it/faq/faq-3.html#3.24> */
    MarkupType.tp_base = &PyUnicode_Type;

    if (PyType_Ready(&MarkupType) < 0)
        return;

    init_constants();

    module = Py_InitModule("_speedups", NULL);
    Py_INCREF(&MarkupType);
    PyModule_AddObject(module, "Markup", (PyObject *) &MarkupType);
}
