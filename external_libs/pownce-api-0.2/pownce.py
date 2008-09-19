"""
A Python interface to the Pownce 2.0 API.

Classes are defined here which model the various types of data the
Pownce API can return, but most uses will simply involve an instance
of ``Api``, which exposes methods for retrieving the data from Pownce
and wraps it up in the appropriate objects.

Example::

    >>> import pownce
    >>> api = pownce.Api('myusername','mypassword','application key')
    >>> public_notes = api.get_public_notes(limit=5)
    >>> public_notes[1]
    <pownce.Message: "All your Wii are belong to Mii!" sent by swiegand at 2007-12-19 23:54:11>
    >>> public_notes[1].sender
    <pownce.User: swiegand>
    >>> public_notes[1].num_recipients
    9L
    >>> ubernostrum = api.get_user(username='ubernostrum')
    >>> ubernostrum
    <pownce.User: ubernostrum>
    >>> ubernostrum.gender
    u'Gentleman'

Currently, ``Api`` implements all features of the Pownce 2.0 API as
described here (as of 2008-03-02):

http://pownce.pbwiki.com/API+Documentation2-2

This module uses the JSON flavor of the API, and requires simplejson
for JSON parsing; simplejson can be obtained from

http://cheeseshop.python.org/pypi/simplejson

or, if Django is installed, the version bundled with it will be
detected and used.

"""

import datetime
import time
import urllib
import urllib2
import gzip
import base64
import mimetools, mimetypes
import os, stat

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    import simplejson
except ImportError:
    from django.utils import simplejson


class PrivacyViolation(Exception):
    """
    Exception raised when the API attempts to access information which
    has been marked private or inaccessible by a user.
    
    """
    pass


class NotFound(Exception):
    """
    Exception raised when the API attempts to access a non-existent
    note or user.
    
    """
    pass


class AuthenticationRequired(Exception):
    """
    Exception raised when the API attempts to access information
    without having the proper authentication.
    """
    pass

class ServerError(Exception):
    """
    Exception raised when the remote server encounters an internal
    error.
    """
    pass

class User(object):
    """
    A Pownce user.
    
    The following attributes are defined here (note that if a given
    user has not supplied an optional profile value, the corresponding
    attribute will be set to ``None``):
    
    ``age``
        The user's age, as a long int.

    ``blurb``
        The user's descriptive blurb, as a string.
    
    ``country``
        The user's country, as a string.

    ``fan_count``
        The number of users who are a fan of this user, as a long int.

    ``fan_of_count``
        The number of users this user is a fan of, as a long int.

    ``first_name``
        The user's first name, as a string.

    ``friend_count``
        The user's friend count, as a long int.
    
    ``gender``
        The user's gender, as a string.
    
    ``location``
        The user's location, as a string.
    
    ``max_upload_mb``
        Number of megabytes available to upload, as a long int.

    ``permalink``
        The permanent URL of the user on Pownce, as a string.
    
    ``raw_user_dict``
        The dictionary, parsed from a Pownce JSON API response, from
        which this ``User`` was constructed.
    
    ``short_name``
        The user's short name (first name plus last initial), as a
        string.
    
    ``username``
        The user's username, as a string.
    
    """
    _string_keys = ['blurb',
                    'country',
                    'first_name',
                    'gender',
                    'location',
                    'permalink',
                    'short_name',
                    'username',
                    ]
    
    _int_keys = ['fan_count',
                 'fan_of_count',
                 'friend_count',
                 'max_upload_mb']
    
    MALE_GENDER_OPTIONS = ['Bloke',
                           'Gentleman',
                           'Guy',
                           'Dude',
                           'Male']
    
    FEMALE_GENDER_OPTIONS = ['Bird',
                             'Chicky-poo',
                             'Female',
                             'Girl',
                             'Lady']
    
    def __init__(self, raw_user_dict):
        self.raw_user_dict = raw_user_dict
        for k in self._string_keys:
            setattr(self, k, raw_user_dict.get(k, None))
        for k in self._int_keys:
            try:
                setattr(self, k, long(raw_user_dict[k]))
            except KeyError:
                setattr(self, k, None)
        if raw_user_dict.get('age'):
            self.age = int(raw_user_dict['age'])
        else:
            self.age = None
        self.is_pro = bool(raw_user_dict['is_pro'])
        self.profile_photo_urls = raw_user_dict.get('profile_photo_urls', {})

    def __repr__(self):
        return '<pownce.User: %s>' % self
    
    def __str__(self):
        return self.username
        
    def has_no_gender(self):
        """
        Returns ``True`` if the user has selected 'None of the Above'
        for gender or has selected no gender, ``False`` otherwise.
        
        """
        return self.gender == 'None of the Above' or self.gender is None
    
    def is_female(self):
        """
        Returns ``True`` if the user has selected a gender option
        likely to be female, ``False`` otherwise.
        
        """
        return self.gender in self.FEMALE_GENDER_OPTIONS
    
    def is_male(self):
        """
        Returns ``True`` if the user has selected a gender option
        likely to be male, ``False`` otherwise.
        
        """
        return self.gender in self.MALE_GENDER_OPTIONS
    
    def is_transgender(self):
        """
        Returns ``True`` if the user has selected 'Transgender' for
        gender, ``False`` otherwise.
        
        """
        return self.gender == 'Transgender'


class Note(object):
    """
    Base class representing attributes common to most types of content
    posted to Pownce.
    
    The following common attributes are defined here:
    
    ``body``
        The body of the note, as a string.
    
    ``display_since``
        The time since the note was posted, as a string
        (e.g., "7 hours ago").
    
    ``id``
        The Pownce ID of the note, as a long integer.

    ``is_public``
        Whether this note is public or not, as a boolean.
    
    ``num_recipients``
        The number of recipients of the note, as a long integer.
    
    ``num_replies``
        The number of replies to the note, as a long integer.
    
    ``permalink``
        The permanent URL of the note on Pownce, as a string.
    
    ``raw_note_dict``
        The dictionary, parsed from a Pownce API JSON response, from
        which this ``Note`` object was constructed.

    ``recipients``
        If the raw note dictionary included information on its
        recipients, a list of ``User`` objects representing all
        recipients whose information was included. ``None`` otherwise.

    ``replies``
        If the raw note dictionary included information on its
        replies, a list of ``Reply`` objects representing all replies
        whose information was included. ``None`` otherwise.
    
    ``seconds_since``
        The number of seconds since the note was posted, as a long
        integer.
    
    ``seconds_since_delta``
        The number of seconds since the note was posted, as a
        ``datetime.timedelta`` object.
    
    ``sender``
        The user who posted the note, as a ``User`` object.
    
    ``stars``
        The rating of the note, as a float.
    
    ``timestamp``
        The timestamp on which the note was posted, in seconds since
        the Unix epoch, as a long integer.
    
    ``timestamp_parsed``
        The timestamp on which the note was posted, as a
        ``datetime.datetime`` object.
    
    ``type``
        The type of the note, as a string. Possible values are
        'event', 'file', 'link', 'message'. See also the constants
        defined on this class (documented below) which represent these
        types.
    
    Additionally, the following constants are defined to represent the
    types of Pownce notes, allowing comparison of the ``type`` of any
    ``Note`` to determine if it is of a specific type.
    
    ``EVENT_TYPE``
        The string representing the event type.
    
    ``LINK_TYPE``
        The string representing the link type.
    
    ``MESSAGE_TYPE``
        The string representing the message type.
    
    """
    EVENT_TYPE = 'event'
    LINK_TYPE = 'link'
    MESSAGE_TYPE = 'message'
    _float_keys = ['stars']
    _int_keys = ['id',
                 'num_recipients',
                 'num_replies',
                 'seconds_since',
                 'timestamp']
    _string_keys = ['body',
                    'display_since',
                    'permalink',
                    'type']

    def __init__(self, raw_note_dict):
        self.raw_note_dict = raw_note_dict
        for k in self._int_keys:
            try:
                setattr(self, k, float(raw_note_dict[k]))
            except KeyError:
                setattr(self, k, None)
        for k in self._int_keys:
            try:
                setattr(self, k, long(raw_note_dict[k]))
            except KeyError:
                setattr(self, k, None)
        for k in self._string_keys:
            setattr(self, k, raw_note_dict[k])
        self.is_public = bool(raw_note_dict['is_public'])
        self.seconds_since_delta = datetime.timedelta(seconds=self.seconds_since)
        self.sender = User(self.raw_note_dict['sender'])
        self.timestamp_parsed = datetime.datetime.fromtimestamp(self.timestamp)
        if 'recipients' in self.raw_note_dict.keys():
            self.recipients = [User(user_dict) for user_dict in self.raw_note_dict['recipients']]
        else:
            self.recipients = None
        if 'replies' in self.raw_note_dict.keys():
            self.replies = [Reply(message_dict, self) for message_dict in self.raw_note_dict['replies']]
        else:
            self.replies = None
    
    def __repr__(self):
        return '<pownce.%s: %s>' % (self.type.capitalize(), self)
    
    def __str__(self):
        return '"%s" sent by %s at %s' % (self.body, self.sender,
                                          self.timestamp_parsed.strftime('%Y-%m-%d %H:%M:%S'))


class Reply(Note):
    """
    A reply to a Pownce note.
    
    Defines only the subset of attributes from ``Note`` which are
    present on replies:
    
    * ``body``
    * ``display_since``
    * ``id``
    * ``seconds_since``
    * ``sender``
    * ``timestamp``
    
    One additional attribute is defined, however:
    
    ``parent``
        The ``Note`` to which this reply is attached.
    
    """
    _int_keys = ['id',
                 'seconds_since',
                 'timestamp']
    _string_keys = ['body',
                    'display_since']
    
    def __init__(self, raw_note_dict, parent):
        self.raw_note_dict = raw_note_dict
        self.parent = parent
        for k in self._int_keys:
            setattr(self, k, long(raw_note_dict[k]))
        for k in self._string_keys:
            setattr(self, k, raw_note_dict[k])
        self.seconds_since_delta = datetime.timedelta(seconds=self.seconds_since)
        self.sender = User(self.raw_note_dict['sender'])
        self.timestamp_parsed = datetime.datetime.fromtimestamp(self.timestamp)
        self.type = 'reply'

    def __str__(self):
        return '"%s" sent by %s in response to %s' % (self.body, self.sender, self.parent)

class Message(Note):
    """
    A Pownce message.
    
    Has all the attributes of ``Note`` (see above).
    
    The ``type`` attribute of instances of this class will always be
    "message".
    
    """
    pass


class Link(Note):
    """
    A Pownce link.
    
    Has all the attributes of ``Note`` (see above), plus one
    additional attribute:
    
    ``link``
        The link URL, as a string.
    
    The ``type`` attribute of instances of this class will always be
    "link".
    
    """
    _string_keys = ['body',
                   'display_since',
                   'permalink',
                   'type']
    def __init__(self, raw_note_dict):
        super(Link, self).__init__(raw_note_dict)
        self.link = self.raw_note_dict['link']['url']


class EventDetails(object):
    """
    Event details of a Pownce event.
    
    The following attributes are defined here:
    
    ``date``
        The date on which the event takes place, as a string.
    
    ``date_parsed``
        The date on which the event takes place, as a
        ``datetime.datetime`` object.
    
    ``ical``
        The iCal URL on Pownce for the event, as a string.
    
    ``location``
        The location of the event, as a string.
    
    ``name``
        The name of the event, as a string.
    
    ``parent``
        The ``Event`` object whose details are represented.
    
    ``raw_event_dict``
        The dictionary, parsed from a Pownce JSON API response, from
        which this ``EventDetails`` object was constructed.
    
    """
    def __init__(self, raw_event_dict, parent):
        self.raw_event_dict = raw_event_dict
        self.parent = parent
        for k, v in self.raw_event_dict.items():
            setattr(self, k, v)
        self.date_parsed = datetime.datetime(*time.strptime(self.date, '%Y-%m-%d %H:%M:%S')[:7])

    def __repr__(self):
        return '<pownce.EventDetails: %s>' % self

    def __str__(self):
        return '"%s" on %s' % (self.name, self.date_parsed.strftime('%Y-%m-%d %H:%M:%S'))
    
    def is_future(self):
        """
        Returns ``True`` if the event takes place in the future,
        ``False`` otherwise.
        
        """
        return self.date_parsed > datetime.datetime.now()
    
    def is_past(self):
        """
        Returns ``True`` if the event took place in the past,
        ``False`` otherwise.
        
        """
        return datetime.datetime.now() > self.date_parsed
    
    def is_today(self):
        """
        Returns ``True`` if the event takes place today, ``False``
        otherwise.
        
        """
        return self.date_parsed.date() == datetime.date.today()
    
    def time_since(self):
        """
        Returns the time since the event took place, as a
        ``datetime.timedelta`` object. If the event has not yet taken
        place, this will be a negative ``timedelta``.
        
        """
        return datetime.datetime.now() - self.date_parsed
    
    def time_until(self):
        """
        Returns the time until the event takes place, as a
        ``datetime.timedelta`` object. If the event has already taken
        place, this will be a negative ``timedelta``.
        
        """
        return self.date_parsed - datetime.datetime.now()


class Event(Note):
    """
    A Pownce event.
    
    Has all the attributes of ``Note`` (see above), plus one extra
    attribute:
    
    ``event``
        The event details, as an ``EventDetails`` object (see above).

    The ``type`` attribute of instances of this class will always be
    "event".
    
    """
    def __init__(self, raw_note_dict):
        super(Event, self).__init__(raw_note_dict)
        self.event = EventDetails(self.raw_note_dict['event'], self)


class FileDetails(object):
    """
    Details of a Pownce file.

    The following attributes are defined here:

    ``content_length``
        The length of the content contained in the file on the server.

    ``content_type``
        The mimetype of the file.

    ``name``
        The file's original filename.  For an image, it could be
        something like 'picture.jpg'.

    ``file_type``
        The type of file.  As an example, this could be 'image'.

    ``url``
        The URL from which to download the file.

    ``parent``
        The ``File`` object whose details are represented.
    
    ``raw_file_dict``
        The dictionary, parsed from a Pownce JSON API response, from
        which this ``FileDetails`` object was constructed.
    """
    def __init__(self, raw_file_dict, parent):
        self.raw_file_dict = raw_file_dict
        self.parent = parent
        for k, v in self.raw_file_dict.items():
            if k == 'type':
                setattr(self, 'file_type', v)
            else:
                setattr(self, k, v)

    def __repr__(self):
        return '<pownce.FileDetails: %s>' % self

    def __str__(self):
        return '%s (%s)' % (self.name, self.file_type)

class File(Note):
    """
    A Pownce event.
    
    Has all the attributes of ``Note`` (see above), plus one extra
    attribute:
    
    ``file_details``
        The file details, as a ``FileDetails`` object (see above).
    """
    def __init__(self, raw_note_dict):
        super(File, self).__init__(raw_note_dict)
        self.file_details = FileDetails(self.raw_note_dict['file'], self)

class Api(object):
    """
    An instance of the Pownce API, which knows how to perform queries
    against it.
    
    Takes three positional arguments:
    
    ``username``
        The username of the User for which the API calls should be 
        made.
    
    ``password``
        The password for the aforementioned User.
    
    ``app_key``
        The application key, as requested at the `Pownce API Page`_.
    
    .. _`Pownce API Page`: http://pownce.com/api/apps/
    """
    API_URL = 'http://api.pownce.com/2.0/'

    OBJECT_TYPE_MAPPING = { 'event': Event,
                            'link': Link,
                            'message': Message,
                            'reply': Message,
                            'file': File }

    ERROR_MAPPING = { 401: AuthenticationRequired,
                      403: PrivacyViolation,
                      404: NotFound,
                      500: ServerError }
    
    def __init__(self, username, password, app_key):
        self.app_key = app_key
        self.username = username
        self.password = password
        self._encode_auth()
    
    def set_username(self, username):
        """
        Sets the username of the User for which the API calls should 
        be made.
        """
        self.username = username
        self._encode_auth()
    
    def set_password(self, password):
        """
        Sets the password for the User for which the API calls should
        be made.
        """
        self.password = password
        self._encode_auth()
    
    def set_app_key(self, app_key):
        """
        Sets the application key, as it appears on the 
        `Pownce API Page`_.
        
        .. _`Pownce API Page`: http://pownce.com/api/apps/
        """
        self.app_key = app_key
        self._encode_auth()
    
    def _encode_auth(self):
        """
        Performs an upfront *Base64* encoding of the username and 
        password supplied by this instance.
        """
        encoded_auth = base64.encodestring("%s:%s" % (self.username, self.password))
        encoded_auth = encoded_auth[:len(encoded_auth)-1]
        self.encoded_auth = encoded_auth
    
    def _note_validation(self, limit, note_type):
        """
        Validates against some common limit and note_type parameters.
        """
        if limit > 100:
            raise ValueError("The Pownce API does not permit retrieval of more than 100 notes at a time")
        if limit is not None and limit < 1:
            raise ValueError("Cannot return less than one note")
        if note_type is not None and note_type not in ('events', 'links', 'messages'):
            raise ValueError("'%s' is not a valid note type. Valid note types are: events, links, messages" % note_type)
    
    def get_public_notes(self, limit=None, page=None, note_type=None, since_id=None):
        """
        Retrieve a list of public notes, as a list of ``Note``
        objects.
        
        Optional arguments:
        
        ``limit``
            The maximum number of notes to retrieve. Defaults to 20 if
            not specified. The Pownce API imposes a maximum of 100
            notes retrieved; attempting to use a higher limit will
            raise a ``ValueError``.
        
        ``page``
            The (zero-indexed) page from which to begin retrieval of
            notes. The number of notes per page is governed by
            ``limit``.
        
        ``note_type``
            The type of note to retrieve. Options are 'events',
            'links' and 'messages'; if unspecified, all types of notes
            will be retrieved.
        
        ``since_id``
            The id of note after which all results will be.  In other
            words, limit the notes returned to those greater than the
            specified note id.

        If ``limit`` and ``page`` combine to produce an invalid or
        nonexistent page, ``NotFound`` will be raised.
        
        """
        self._note_validation(limit, note_type)
        
        query_dict = {'app_key' : self.app_key}
        if limit is not None:
            query_dict['limit'] = limit
        if page is not None:
            query_dict['page'] = page
        if note_type is not None:
            query_dict['type'] = note_type
        if since_id is not None:
            query_dict['since_id'] = since_id
        
        url = '%snote_lists.json?%s' % (self.API_URL, urllib.urlencode(query_dict))
        
        json_obj = simplejson.loads(self._fetch(url))
        if 'notes' in json_obj.keys():
            object_list = []
            for pownce_obj in json_obj['notes']:
                obj_type = self.OBJECT_TYPE_MAPPING[pownce_obj['type']]
                object_list.append(obj_type(pownce_obj))
            return object_list
        else:
            raise NotFound("Error retrieving notes: %s" % json_obj['error']['message'])
    
    def get_notes(self, username, note_type=None, limit=None, page=None, since_id=None,
                  note_filter=None, note_set=None):
        """
        Retrieve a list of notes for the given username, as a list of
        ``Note`` objects.
        
        Required arguments:
        
        ``username``
            The username of the User for which to get notes.
        
        Optional arguments:
        
        ``note_type``
            The type of note to retrieve. Options are 'events',
            'links' and 'messages'; if unspecified, all types of notes
            will be retrieved.
        
        ``limit``
            The maximum number of notes to retrieve. Defaults to 20 if
            not specified. The Pownce API imposes a maximum of 100
            notes retrieved; attempting to use a higher limit will
            raise a ``ValueError``.
        
        ``page``
            The (zero-indexed) page from which to begin retrieval of
            notes. The number of notes per page is governed by
            ``limit``.
        
        ``since_id``
            The id of note after which all results will be.  In other
            words, limit the notes returned to those greater than the
            specified note id.
        
        ``note_filter``:
            Specify a subset of the authenticated user's note list.
            Options are 'notes' (no replies), 'replies', 'sent', 
            'public', 'private', 'nonpublic' (private and 
            friends-only notes), and 'all'. If no filter is 
            specified, the notes will be returned according to the 
            user's preferences.
        
        ``note_set``:
            Specify a filter the authenticated user's notes by a 
            particular set. **Only available for the authenticated 
            user's own notes.**
        
        If ``limit``, ``page``, ``since_id``, ``note_filter``, and 
        ``note_set`` combine to produce an invalid or nonexistent 
        page, ``NotFound`` will be raised.
        """
        self._note_validation(limit, note_type)
        filter_types = ('notes', 'replies','sent', 'public', 'private', 'nonpublic', 'all')
        if note_filter is not None and note_filter not in filter_types:
            raise ValueError("'%s' is not a valid filter type. Valid note types are: %s." 
                % (note_type, ', '.join(filter_types)))
        if note_set and not (self.username == username):
            raise ValueError("Set filtering is only available on the authenticated user's own notes.")
        
        query_dict = {'app_key' : self.app_key}
        if note_type is not None:
            query_dict['type'] = note_type
        if limit is not None:
            query_dict['limit'] = limit
        if page is not None:
            query_dict['page'] = page
        if since_id is not None:
            query_dict['since_id'] = since_id
        if note_filter is not None:
            query_dict['filter'] = note_filter
        if note_set is not None:
            query_dict['set'] = note_set
        
        url = '%snote_lists/%s.json?%s' % (self.API_URL, 
                                           username, 
                                           urllib.urlencode(query_dict))
        
        json_obj = simplejson.loads(self._fetch(url))
        if 'notes' in json_obj.keys():
            object_list = []
            for pownce_obj in json_obj['notes']:
                obj_type = self.OBJECT_TYPE_MAPPING[pownce_obj['type']]
                object_list.append(obj_type(pownce_obj))
            return object_list
        else:
            raise NotFound("Error retrieving notes: %s" % json_obj['error']['message'])
    
    def get_note(self, note_id, show_replies=False, recipient_limit=None):
        """
        Retrieve a public note, returning a ``Note`` object.
        
        Required arguments:
        
        ``note_id``
            The Pownce ID of the note to retrieve.
        
        Optional arguments:
        
        ``show_replies``
            If ``True``, replies to the note will be included in the
            result. Defaults to ``False`` if not supplied.
        
        ``recipient_limit``
            The number of recipients to include (as ``User`` objects)
            on the result. By default, no recipients will be included;
            the maximum permitted is 100.
        
        If the requested note is non-public, raises
        ``PrivacyViolation``.
        
        If the requested note does not exist, raises ``NotFound``.
        
        """
        if recipient_limit > 100:
            raise ValueError("The Pownce API does not permit retrieval of more than 100 recipients at a time")
        
        query_dict = {'app_key' : self.app_key}
        if show_replies:
            query_dict['show_replies'] = 'true'
        if recipient_limit is not None:
            query_dict['recipient_limit'] = recipient_limit

        url = '%snotes/%s.json?%s' % (self.API_URL, note_id, urllib.urlencode(query_dict))
        
        json_obj = simplejson.loads(self._fetch(url))
        if 'type' in json_obj.keys():
            obj_type = self.OBJECT_TYPE_MAPPING[json_obj['type']]
            return obj_type(json_obj)
        elif 'error' in json_obj.keys():
            error_class = self.ERROR_MAPPING[json_obj['error']]
            error_list = (note_id, error['message'])
            raise error_class("Error retrieving note %s: %s" % error_list)

    def get_note_recipients(self, note_id, limit=None, page=None):
        """
        Gets a list of users who have received the specified note, as
        a list of ``User`` objects.
        
        Required arguments:
        
        ``note_id``:
            The Pownce ID of the note to retrieve.
        
        Optional Arguments:
        
        ``limit``
            The maximum number of recipients to retrieve. Defaults to
            20 if not specified. The Pownce API imposes a maximum of 
            100 recipients retrieved; attempting to use a higher 
            limit will raise a ``ValueError``.
        
        ``page``
            The (zero-indexed) page from which to begin retrieval of
            recipients. The number of recipients per page is governed
            by ``limit``.
        
        If ``limit`` and ``page`` combine to produce an invalid or
        nonexistent page, ``NotFound`` will be raised.
        """
        if limit > 100:
            raise ValueError("The Pownce API does not permit retrieval of more than 100 recipients at a time")
        
        query_dict = {'app_key' : self.app_key}
        if limit is not None:
            query_dict['limit'] = limit
        if page is not None:
            query_dict['page'] = page

        url = '%snotes/%s/recipients.json?%s' % (self.API_URL, 
                                                 note_id, 
                                                 urllib.urlencode(query_dict))
        
        json_obj = simplejson.loads(self._fetch(url))
        if 'users' in json_obj.keys():
            return [User(user_dict) for user_dict in json_obj]
        elif 'error' in json_obj.keys():
            error_class = self.ERROR_MAPPING[json_obj['error']]
            raise error_class("Error retrieving note recipients: %s" % error['message'])

    def get_user(self, username):
        """
        Retrieve a Pownce user by username, returning a ``User``
        object.
        
        If the requested user does not exist, raises ``NotFound``.
        
        """
        query_dict = {'app_key' : self.app_key}
        url = '%susers/%s.json?%s' % (self.API_URL, username, urllib.urlencode(query_dict))
        json_obj = simplejson.loads(self._fetch(url))
        if 'error' in json_obj.keys():
            error_class = self.ERROR_MAPPING[json_obj['error']]
            error_list = (username, error['message'])
            raise error_class("Error retrieving user '%s': %s" % error_list)
        return User(json_obj)

    def get_related_users(self, username, relationship, limit=None, page=None):
        """
        Retrieve users related to a particular user.
        
        Required arguments:
        
        ``username``
            The username of the user to fetch relationship information
            for.
        
        ``relationship``
            The type of related users to retrieve. Possible values are
            'fan_of', 'fans', 'friends'.
        
        Optional arguments:
        
        ``limit``
            The number of users to retrieve. Defaults to 20 if not
            specified. The Pownce API imposes a maximum of 100 users
            retrieved; attempting to use a higher limit will raise a
            ``valueError``.
        
        ``page``
            The (zero-indexed) page from which to begin retrieval of
            users. The number of users per page is governed by
            ``limit``.
        
        If the user has marked their friend list non-public, raises
        ``PrivacyViolation``.
        
        If the user does not exist, raises ``NotFound``.
        
        """
        if relationship not in ('friends', 'fans', 'fan_of'):
            raise ValueError("'%s' is not a valid relationship type. Valid relationship types are: friends, fans, fan_of")
        if limit is not None and limit < 1:
            raise ValueError("Cannot return less then one User")
        if limit > 100:
            raise ValueError("The Pownce API does not permit retrieval of more than 100 notes at a time")
        
        query_dict = {'app_key' : self.app_key}
        if limit is not None:
            query_dict['limit'] = limit
        if page is not None:
            query_dict['page'] = page
        
        url = '%susers/%s/%s.json?%s' % (self.API_URL, 
                                         username, 
                                         relationship, 
                                         urllib.urlencode(query_dict))
        
        json_obj = simplejson.loads(self._fetch(url))
        if 'users' in json_obj.keys():
            return [User(user_dict) for user_dict in json_obj]
        elif 'error' in json_obj.keys():
            error_class = self.ERROR_MAPPING[json_obj['error']]
            error_list = (username, error['message'])
            raise error_class("Error retrieving related users for '%s': %s" % error_list)
    
    def send_to_list(self):
        """
        Gets the list of potential recipients for the authenticated user.
        """
        query_dict = {'app_key' : self.app_key}
        url = '%ssend/send_to.json?%s' % (self.API_URL, urllib.urlencode(query_dict))
        json_obj = simplejson.loads(self._fetch(url))
        if 'users' in json_obj.keys():
            return [User(user_dict) for user_dict in json_obj]
        elif 'error' in json_obj.keys():
            error_class = self.ERROR_MAPPING[json_obj['error']]
            raise error_class("Error retrieving 'send_to' list: %s" % error['message'])

    def post_message(self, note_to, note_body):
        """
        Posts a message to Pownce.

        Required arguments:
        
        ``note_to``
            Specifies to whom the note will be sent.  Valid choices
            are 'public', 'all', "friend_x', 'set_x', where x is the
            username or set name, respectively.

        ``note_body``
            The body of the message to be posted to Pownce.
        """
        return self._post_note(note_to, 
                               'message', 
                               note_body=note_body)

    def post_link(self, note_to, url, note_body=None):
        """
        Posts a link to Pownce.

        Required arguments:
        
        ``note_to``
            Specifies to whom the note will be sent.  Valid choices
            are 'public', 'all', "friend_x', 'set_x', where x is the
            username or set name, respectively.

        ``url``:
            The URL to post as the link.
        
        Optional arguments:

        ``note_body``
            The body of the message to be posted to Pownce.
        """
        return self._post_note(note_to, 
                               'link',
                               url=url,
                               note_body=note_body)

    def post_event(self, note_to, event_name, event_location, event_date, note_body=None):
        """
        Posts an event to Pownce.

        Required arguments:
        
        ``note_to``
            Specifies to whom the note will be sent.  Valid choices
            are 'public', 'all', "friend_x', 'set_x', where x is the
            username or set name, respectively.

        ``event_name``:
            The name of the event to be posted.
        
        ``event_location``:
            The location of the event to be posted.
        
        ``event_date``:
            The date of the event to be posted.  Must be a datetime 
            object.
        
        Optional arguments:

        ``note_body``
            The body of the message to be posted to Pownce.
        """
        return self._post_note(note_to, 
                               'event',
                               event_name=event_name,
                               event_location=event_location,
                               event_date=event_date,
                               note_body=note_body)

    def post_file(self, note_to, media_filename, note_body=None):
        """
        Posts a file to Pownce.

        Required arguments:
        
        ``note_to``
            Specifies to whom the note will be sent.  Valid choices
            are 'public', 'all', "friend_x', 'set_x', where x is the
            username or set name, respectively.
    
        ``media_filename``:
            The filename of the file to post, as a string.
        
        Optional arguments:
        
        ``note_body``
            The body of the message to be posted to Pownce.
        """
        return self._post_note(note_to, 
                               'file', 
                               note_body=note_body, 
                               media_filename=media_filename)

    def _post_note(self, note_to, note_type, note_body=None, url=None, event_name=None,
                  event_location=None, event_date=None, media_filename=None):
        """
        Internal API used to post notes of any type to Pownce.
        """
        is_valid = False
        for option in ('public','all','friend_','set_'):
            if note_to.startswith(option):
                is_valid = True
                break
        if is_valid is False:
            raise ValueError("Invalid note_to parameter.")
        
        query_dict = {'app_key': self.app_key}
        
        postdata = { 'note_to': note_to }
        if note_body is not None:
            postdata['note_body'] = note_body
        if note_type == 'link':
            postdata['url'] = url
        elif note_type == 'event':
            postdata['event_name'] = event_name
            postdata['event_location'] = event_location
            postdata['event_date'] = event_date.strftime('%Y-%m-%d %H:%M:%S')
        elif note_type == 'file':
            postdata['media_file'] = (open(media_filename, 'r'), media_filename)
            user = self.get_user(self.username)
            if user.is_pro:
                note_type = 'file_pro'

        api_url = '%ssend/%s.json?%s' % (self.API_URL, 
                                         note_type, 
                                         urllib.urlencode(query_dict))
        json_obj = simplejson.loads(self._fetch(api_url, postdata=postdata))
        if 'type' in json_obj.keys():
            obj_type = self.OBJECT_TYPE_MAPPING[json_obj['type']]
            return obj_type(json_obj)
        elif 'error' in json_obj.keys():
            error_class = self.ERROR_MAPPING[json_obj['error']]
            raise error_class("Error posting note: %s" % error['message'])
        

    def _fetch(self, url, postdata=None, user_agent="python-pownce-api"):
        """
        Fetches results from the Pownce API, using basic
        authentication and accepting gzip encoding.  Also, this will
        POST form data as multipart if there is any POST data to
        post.
        """
        request = urllib2.Request(url)
        request.add_header('User-Agent', user_agent)
        request.add_header('Accept-Encoding', 'gzip')
        request.add_header('Authorization', 'Basic %s' % self.encoded_auth)
        if postdata is not None:
            if 'media_file' in postdata.keys():
                bound = mimetools.choose_boundary()
                ctype = 'multipart/form-data; boundary=%s' % bound
                if hasattr(request, 'add_undirected_header'):
                    header_method = request.add_undirected_header
                else:
                    header_method = request.add_header
                header_method('Content-Type', ctype)
                data = StringIO()
                for (key, value) in postdata.items():
                    if key == 'media_file':
                        (f, filename) = value
                        mime = mimetypes.guess_type(filename)[0]
                        if mime is None:
                            mime = 'application/octet-stream'
                        data.write('--%s\r\nContent-Disposition: form-data; ' % bound)
                        data.write('name="%s"; filename="%s"\r\n' % (key, filename))
                        data.write('Content-Type: %s\r\n\r\n' % mime)
                        data.write('%s\r\n' % f.read())
                    else:
                        data.write('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (bound, key, value))
                data.write('--%s--\r\n\r\n' % bound)
                data = data.getvalue()
            else:
                data = urllib.urlencode(postdata.items(), 1)
            request.add_data(data)
        opener = urllib2.build_opener()
        f = opener.open(request)
        result = f.read()
        if f.headers.get('content-encoding', '') == 'gzip':
            result = gzip.GzipFile(fileobj=StringIO(result)).read()
        f.close()
        return result
