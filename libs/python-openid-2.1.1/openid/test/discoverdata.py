"""Module to make discovery data test cases available"""
import urlparse
import os.path

from openid.yadis.discover import DiscoveryResult, DiscoveryFailure
from openid.yadis.constants import YADIS_HEADER_NAME

tests_dir = os.path.dirname(__file__)
data_path = os.path.join(tests_dir, 'data')

testlist = [
# success,  input_name,          id_name,            result_name
    (True,  "equiv",             "equiv",            "xrds"),
    (True,  "header",            "header",           "xrds"),
    (True,  "lowercase_header",  "lowercase_header", "xrds"),
    (True,  "xrds",              "xrds",             "xrds"),
    (True,  "xrds_ctparam",      "xrds_ctparam",     "xrds_ctparam"),
    (True,  "xrds_ctcase",       "xrds_ctcase",      "xrds_ctcase"),
    (False, "xrds_html",         "xrds_html",        "xrds_html"),
    (True,  "redir_equiv",       "equiv",            "xrds"),
    (True,  "redir_header",      "header",           "xrds"),
    (True,  "redir_xrds",        "xrds",             "xrds"),
    (False, "redir_xrds_html",   "xrds_html",        "xrds_html"),
    (True,  "redir_redir_equiv", "equiv",            "xrds"),
    (False, "404_server_response", None,             None),
    (False, "404_with_header",     None,             None),
    (False, "404_with_meta",       None,             None),
    (False, "201_server_response", None,             None),
    (False, "500_server_response", None,             None),
    ]

def getDataName(*components):
    sanitized = []
    for part in components:
        if part in ['.', '..']:
            raise ValueError
        elif part:
            sanitized.append(part)

    if not sanitized:
        raise ValueError

    return os.path.join(data_path, *sanitized)

def getExampleXRDS():
    filename = getDataName('example-xrds.xml')
    return file(filename).read()

example_xrds = getExampleXRDS()
default_test_file = getDataName('test1-discover.txt')

discover_tests = {}

def readTests(filename):
    data = file(filename).read()
    tests = {}
    for case in data.split('\f\n'):
        (name, content) = case.split('\n', 1)
        tests[name] = content
    return tests

def getData(filename, name):
    global discover_tests
    try:
        file_tests = discover_tests[filename]
    except KeyError:
        file_tests = discover_tests[filename] = readTests(filename)
    return file_tests[name]

def fillTemplate(test_name, template, base_url, example_xrds):
    mapping = [
        ('URL_BASE/', base_url),
        ('<XRDS Content>', example_xrds),
        ('YADIS_HEADER', YADIS_HEADER_NAME),
        ('NAME', test_name),
        ]

    for k, v in mapping:
        template = template.replace(k, v)

    return template

def generateSample(test_name, base_url,
                   example_xrds=example_xrds,
                   filename=default_test_file):
    try:
        template = getData(filename, test_name)
    except IOError, why:
        import errno
        if why[0] == errno.ENOENT:
            raise KeyError(filename)
        else:
            raise

    return fillTemplate(test_name, template, base_url, example_xrds)

def generateResult(base_url, input_name, id_name, result_name, success):
    input_url = urlparse.urljoin(base_url, input_name)

    # If the name is None then we expect the protocol to fail, which
    # we represent by None
    if id_name is None:
        assert result_name is None
        return input_url, DiscoveryFailure

    result = generateSample(result_name, base_url)
    headers, content = result.split('\n\n', 1)
    header_lines = headers.split('\n')
    for header_line in header_lines:
        if header_line.startswith('Content-Type:'):
            _, ctype = header_line.split(':', 1)
            ctype = ctype.strip()
            break
    else:
        ctype = None

    id_url = urlparse.urljoin(base_url, id_name)

    result = DiscoveryResult(input_url)
    result.normalized_uri = id_url
    if success:
        result.xrds_uri = urlparse.urljoin(base_url, result_name)
    result.content_type = ctype
    result.response_text = content
    return input_url, result
