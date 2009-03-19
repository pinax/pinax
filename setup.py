from setuptools import setup, find_packages

setup(
    name='Pinax',
    version=__import__('pinax').__version__,
    description='Pinax is an open-source collection of re-usable apps for the Django Web Framework',
    long_description=open('docs/intro.txt').read(),
    author='James Tauber',
    author_email='jtauber@jtauber.com',
    maintainer='Jannis Leidel',
    maintainer_email='jannis@leidel.info',
    url='http://pinaxproject.com/',
    packages=find_packages(),
    include_package_data=True, # include package data under svn source control
    setup_requires=['setuptools_git'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pinax-clone-project = pinax.conf.clone_project:entry_point',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: JavaScript',
    ],
)
