# Source and destination file names.
test_source = "field_list.txt"
test_destination = "field_name_limit.html"

# Keyword parameters passed to publish_file.
reader_name = "standalone"
parser_name = "rst"
writer_name = "html"

# Settings
settings_overrides['field_name_limit'] = 0 # no limit
settings_overrides['docinfo_xform'] = 0
