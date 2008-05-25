"""
This package is an implementation of the OpenID specification in
Python.  It contains code for both server and consumer
implementations.  For information on implementing an OpenID consumer,
see the C{L{openid.consumer.consumer}} module.  For information on
implementing an OpenID server, see the C{L{openid.server.server}}
module.

@contact: U{dev@lists.openidenabled.com
    <http://lists.openidenabled.com/mailman/listinfo/dev>}

@copyright: (C) 2005-2007 JanRain, Inc.

@license: Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    U{http://www.apache.org/licenses/LICENSE-2.0}

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions
    and limitations under the License.
"""

__version__ = '[library version:2.1.1]'[17:-1]

# Parse the version info
try:
    version_info = map(int, __version__.split('.'))
except ValueError:
    version_info = (None, None, None)
else:
    if len(version_info) != 3:
        version_info = (None, None, None)
    else:
        version_info = tuple(version_info)
