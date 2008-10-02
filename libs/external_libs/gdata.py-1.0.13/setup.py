#!/usr/bin/python
#
# Copyright (C) 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from distutils.core import setup


setup(
    name='gdata.py',
    version='1.0.13',
    description='Python client library for Google data APIs',
    long_description = """\
The Google data Python client library makes it easy to access data
through the Google data APIs. This library provides data model and
service modules for the the following Google data services:
- Google Calendar data API
- Google Contacts data API
- Google Spreadsheets data API
- Google Document List data APIs
- Google Base data API
- Google Apps Provisioning API
- Picasa Web Albums Data API
- Google Code Search Data API
- core Google data API functionality 
The core Google data code provides sufficient functionality to use this 
library with any Google data API (even if a module hasn't been written for 
it yet). For example, this client can be used with the Blogger API, and the
YouTube API. This library may also be used with any Atom Publishing Protocol
service.
""",
    author='Jeffrey Scudder',
    author_email='api.jscudder@gmail.com',
    license='Apache 2.0',
    url='http://code.google.com/p/gdata-python-client/',
    packages=['atom', 'gdata', 'gdata.calendar', 'gdata.base',
        'gdata.spreadsheet', 'gdata.apps', 'gdata.docs', 'gdata.codesearch',
        'gdata.photos', 'gdata.exif', 'gdata.geo', 'gdata.media', 
        'gdata.contacts'],
    package_dir = {'gdata':'src/gdata', 'atom':'src/atom'}
)
