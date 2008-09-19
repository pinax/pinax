# Source and destination file names.
test_source = "pep_html.txt"
test_destination = "pep_html.html"

# Keyword parameters passed to publish_file.
reader_name = "pep"
parser_name = "rst"
writer_name = "pep_html"

# Settings
settings_overrides['python_home'] = "http://www.python.org"
settings_overrides['pep_home'] = "http://www.python.org/peps"
settings_overrides['no_random'] = 1
settings_overrides['cloak_email_addresses'] = 1
