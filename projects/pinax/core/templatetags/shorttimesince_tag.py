from django.template import Library
register = Library()

import datetime
import time

from django.utils.tzinfo import LocalTimezone
from django.utils.translation import ungettext, ugettext

def calculate_shorttimesince(d, now=None):
    """
    like django's built in timesince but abbreviates units
    """
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ungettext('yr', 'yr', n)),
      (60 * 60 * 24 * 30, lambda n: ungettext('mn', 'mn', n)),
      (60 * 60 * 24 * 7, lambda n : ungettext('wk', 'wk', n)),
      (60 * 60 * 24, lambda n : ungettext('d', 'd', n)),
      (60 * 60, lambda n: ungettext('hr', 'hr', n)),
      (60, lambda n: ungettext('min', 'min', n))
    )
    # Convert datetime.date to datetime.datetime for comparison
    if d.__class__ is not datetime.datetime:
        d = datetime.datetime(d.year, d.month, d.day)
    if now:
        t = now.timetuple()
    else:
        t = time.localtime()
    if d.tzinfo:
        tz = LocalTimezone(d)
    else:
        tz = None
    now = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5], tzinfo=tz)

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return u'0' + ugettext('min')
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    s = ugettext('%(number)d%(type)s') % {'number': count, 'type': name(count)}
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            s += ugettext(', %(number)d%(type)s') % {'number': count2, 'type': name2(count2)}
    return s
    
def shorttimesince(value, arg=None):
    """Formats a date as the time since that date (i.e. "4 days, 6 hours")."""
    from django.utils.timesince import timesince
    if not value:
        return u''
    if arg:
        return calculate_shorttimesince(arg, value)
    return calculate_shorttimesince(value)
shorttimesince.is_safe = False

register.filter(shorttimesince)
