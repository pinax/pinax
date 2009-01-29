from setuptools import setup

setup(
    name='diff-match-patch',
    version='20090110',
    author='Neil Fraser',
    url='http://code.google.com/p/google-diff-match-patch/',
    py_modules=['diff_match_patch'],
    test_suite='diff_match_patch_test.DiffMatchPatchTest',
)
