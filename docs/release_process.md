# Release Process

Script https://github.com/pinax/pinax/blob/master/check.py can help identify which apps need releases. Be sure to install requirements as specified.

* make sure all issues are triaged
* make sure all pull-requests are triaged
* establish new version number based on semver
* update docs/changelog.md
* make sure AUTHORS is up-to-date for new contributions
* update setup.py
* confirm Travis CI passed
* do a release on GitHub with tag of form `v1.2.3` and release name of `1.2.3`, using the changelog entry for the release notes
* do `git clean -fdx`
* publish to pypi with `python setup.py sdist bdist_wheel upload`

    Note: if this command fails with `error: invalid command 'bdist_wheel'`
    you need to install "wheel" in your virtualenv:
    
        `$ pip install wheel`

see also https://github.com/pinax/pinax/issues/113
