import os
from setuptools import setup, find_packages

VERSION = __import__('pinax').__version__

def read(*path):
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *path)).read()

setup(
    name='Pinax',
    version=VERSION,
    description='Pinax is an open-source collection of re-usable apps for the Django Web Framework',
    long_description=read('docs', 'intro.txt'),
    author='James Tauber',
    author_email='jtauber@jtauber.com',
    maintainer='Jannis Leidel',
    maintainer_email='jannis@leidel.info',
    url='http://pinaxproject.com/',
    packages=find_packages(),
    include_package_data=True,
    # Ignore the tarballs we built our own in a source distribution
    exclude_package_data={
        'requirements': ['%s/*.tar.gz' % VERSION],
    },
    zip_safe=False,
    setup_requires=[
        'setuptools_dummy',
    ],
    entry_points={
        'console_scripts': [
            'pinax-admin = pinax.core.management:execute_from_command_line',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: JavaScript',
    ],
)
