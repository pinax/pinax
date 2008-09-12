# This module provides helper functions for the JSON part of your
# view, if you are providing a JSON-based API for your app.

# Here's what most rules would look like:
# @jsonify.when("isinstance(obj, YourClass)")
# def jsonify_yourclass(obj):
#     return [obj.val1, obj.val2]
#
# The goal is to break your objects down into simple values:
# lists, dicts, numbers and strings

from turbojson.jsonify import jsonify

