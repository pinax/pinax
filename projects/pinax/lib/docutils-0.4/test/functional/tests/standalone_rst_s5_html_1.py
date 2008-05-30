execfile('functional/tests/_standalone_rst_defaults.py')

# Source and destination file names:
test_source = 'standalone_rst_s5_html.txt'
test_destination = 'standalone_rst_s5_html_1.html'

# Keyword parameters passed to publish_file:
writer_name = 's5_html'

# Settings:
settings_overrides['theme'] = 'small-black'


# Extra functional tests.
# Prefix all names with '_' to avoid confusing `docutils.core.publish_file`.

import filecmp as _filecmp

def _test_more(expected_dir, output_dir, test_case, parameters):
    """Compare ``ui/<theme>`` directories."""
    theme = settings_overrides.get('theme', 'default')
    expected = '%s/%s/%s' % (expected_dir, 'ui', theme)
    output = '%s/%s/%s' % (output_dir, 'ui', theme)
    differences, uniques = _compare_directories(expected, output)
    parts = []
    if differences:
        parts.append('The following files differ from the expected output:')
        parts.extend(differences)
        expected = [path.replace('functional/output/', 'functional/expected/')
                    for path in differences]
        parts.append('Please compare the expected and actual output files:')
        parts.extend(['  diff %s %s' % tup
                      for tup in zip(expected, differences)])
        parts.append('If the actual output is correct, please replace the '
                     'expected output files:')
        parts.extend(['  mv %s %s' % tup
                      for tup in zip(differences, expected)])
        parts.append('and check them in to Subversion:')
        parts.extend(['  svn commit -m "<comment>" %s' % path
                      for path in expected])
    if uniques:
        parts.append('The following paths are unique:')
        parts.extend(uniques)
    test_case.assert_(not parts, '\n'.join(parts))

def _compare_directories(expected, output):
    dircmp = _filecmp.dircmp(expected, output, ['.svn', 'CVS'])
    differences = ['%s/%s' % (output, name) for name in dircmp.diff_files]
    uniques = (['%s/%s' % (expected, name) for name in dircmp.left_only]
               + ['%s/%s' % (output, name) for name in dircmp.right_only])
    for subdir in dircmp.common_dirs:
        diffs, uniqs = _compare_directories('%s/%s' % (expected, subdir),
                                            '%s/%s' % (output, subdir))
        differences.extend(diffs)
        uniques.extend(uniqs)
    return differences, uniques
