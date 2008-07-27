# Source and destination file names.
test_source = "latex_docinfo.txt"
test_destination = "latex_docinfo.tex"

# Keyword parameters passed to publish_file.
reader_name = "standalone"
parser_name = "rst"
writer_name = "latex"

# Extra setting we need

settings_overrides['use_latex_docinfo'] = 1
