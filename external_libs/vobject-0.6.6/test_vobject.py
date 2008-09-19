"""Long or boring tests for vobjects."""

import vobject
from vobject import base, icalendar, behavior, vcard, hcalendar
import StringIO, re, dateutil.tz, datetime

import doctest, test_vobject, unittest

from pkg_resources import resource_stream

base.logger.setLevel(base.logging.FATAL)
#------------------- Testing and running functions -----------------------------
# named additional_tests for setuptools
def additional_tests():

    flags = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
    suite = unittest.TestSuite()
    for module in base, test_vobject, icalendar, vobject, vcard:
        suite.addTest(doctest.DocTestSuite(module, optionflags=flags))

    suite.addTest(doctest.DocFileSuite(
        'README.txt', 'test_files/more_tests.txt',
        package='__main__', optionflags=flags
    ))
    return suite
    
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(additional_tests())


testSilly="""
sillyname:name
profile:sillyprofile
stuff:folded
 line
""" + "morestuff;asinine:this line is not folded, \
but in practice probably ought to be, as it is exceptionally long, \
and moreover demonstratively stupid"

icaltest=r"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
X-WR-TIMEZONE;VALUE=TEXT:US/Pacific
METHOD:PUBLISH
PRODID:-//Apple Computer\, Inc//iCal 1.0//EN
X-WR-CALNAME;VALUE=TEXT:Example
VERSION:2.0
BEGIN:VEVENT
SEQUENCE:5
DTSTART;TZID=US/Pacific:20021028T140000
RRULE:FREQ=Weekly;COUNT=10
DTSTAMP:20021028T011706Z
SUMMARY:Coffee with Jason
UID:EC9439B1-FF65-11D6-9973-003065F99D04
DTEND;TZID=US/Pacific:20021028T150000
BEGIN:VALARM
TRIGGER;VALUE=DURATION:-P1D
ACTION:DISPLAY
DESCRIPTION:Event reminder\, with comma\nand line feed
END:VALARM
END:VEVENT
BEGIN:VTIMEZONE
X-LIC-LOCATION:Random location
TZID:US/Pacific
LAST-MODIFIED:19870101T000000Z
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0700
TZOFFSETTO:-0800
TZNAME:PST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
TZNAME:PDT
END:DAYLIGHT
END:VTIMEZONE
END:VCALENDAR"""

badDtStartTest="""BEGIN:VCALENDAR
METHOD:PUBLISH
VERSION:2.0
BEGIN:VEVENT
DTSTART:20021028
DTSTAMP:20021028T011706Z
SUMMARY:Coffee with Jason
UID:EC9439B1-FF65-11D6-9973-003065F99D04
END:VEVENT
END:VCALENDAR"""

badLineTest="""BEGIN:VCALENDAR
METHOD:PUBLISH
VERSION:2.0
BEGIN:VEVENT
DTSTART:19870405T020000
X-BAD/SLASH:TRUE
X-BAD_UNDERSCORE:TRUE
UID:EC9439B1-FF65-11D6-9973-003065F99D04
END:VEVENT
END:VCALENDAR"""

vcardtest =r"""BEGIN:VCARD
VERSION:3.0
FN:Daffy Duck Knudson (with Bugs Bunny and Mr. Pluto)
N:Knudson;Daffy Duck (with Bugs Bunny and Mr. Pluto)
NICKNAME:gnat and gnu and pluto
BDAY;value=date:02-10
TEL;type=HOME:+01-(0)2-765.43.21
TEL;type=CELL:+01-(0)5-555.55.55
ACCOUNT;type=HOME:010-1234567-05
ADR;type=HOME:;;Haight Street 512\;\nEscape\, Test;Novosibirsk;;80214;Gnuland
TEL;type=HOME:+01-(0)2-876.54.32
ORG:University of Novosibirsk\, Department of Octopus
  Parthenogenesis
END:VCARD"""

vcardWithGroups = r"""home.begin:vcard
version:3.0
source:ldap://cn=Meister%20Berger,o=Universitaet%20Goerlitz,c=DE
name:Meister Berger
fn:Meister Berger
n:Berger;Meister
bday;value=date:1963-09-21
o:Universit=E6t G=F6rlitz
title:Mayor
title;language=de;value=text:Burgermeister
note:The Mayor of the great city of 
  Goerlitz in the great country of Germany.\nNext line.
email;internet:mb@goerlitz.de
home.tel;type=fax,voice;type=msg:+49 3581 123456
home.label:Hufenshlagel 1234\n
 02828 Goerlitz\n
 Deutschland
END:VCARD"""

lowercaseComponentNames = r"""begin:vcard
fn:Anders Bobo
n:Bobo;Anders
org:Bobo A/S;Vice President, Technical Support
adr:Rockfeller Center;;Mekastreet;Bobocity;;2100;Myworld
email;internet:bobo@example.com
tel;work:+123455
tel;fax:+123456
tel;cell:+123457
x-mozilla-html:FALSE
url:http://www.example.com
version:2.1
end:vcard"""

icalWeirdTrigger = r"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
X-WR-TIMEZONE;VALUE=TEXT:US/Pacific
METHOD:PUBLISH
PRODID:-//Apple Computer\, Inc//iCal 1.0//EN
X-WR-CALNAME;VALUE=TEXT:Example
VERSION:2.0
BEGIN:VEVENT
DTSTART:20021028T140000Z
BEGIN:VALARM
TRIGGER:20021028T120000Z
ACTION:DISPLAY
DESCRIPTION:This trigger is a date-time without a VALUE=DATE-TIME parameter
END:VALARM
END:VEVENT
END:VCALENDAR"""

badstream = r"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
X-WR-TIMEZONE;VALUE=TEXT:US/Pacific
METHOD:PUBLISH
PRODID:-//Apple Computer\, Inc//iCal 1.0//EN
X-WR-CALNAME;VALUE=TEXT:Example
VERSION:2.0
BEGIN:VEVENT
DTSTART:20021028T140000Z
BEGIN:VALARM
TRIGGER:a20021028120000
ACTION:DISPLAY
DESCRIPTION:This trigger has a nonsensical value
END:VALARM
END:VEVENT
END:VCALENDAR"""

timezones = r"""

BEGIN:VTIMEZONE
TZID:US/Pacific
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0700
TZOFFSETTO:-0800
TZNAME:PST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
TZNAME:PDT
END:DAYLIGHT
END:VTIMEZONE

BEGIN:VTIMEZONE
TZID:US/Eastern
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
END:DAYLIGHT
END:VTIMEZONE

BEGIN:VTIMEZONE
TZID:Santiago
BEGIN:STANDARD
DTSTART:19700314T000000
TZOFFSETFROM:-0300
TZOFFSETTO:-0400
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SA
TZNAME:Pacific SA Standard Time
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19701010T000000
TZOFFSETFROM:-0400
TZOFFSETTO:-0300
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=2SA
TZNAME:Pacific SA Daylight Time
END:DAYLIGHT
END:VTIMEZONE

BEGIN:VTIMEZONE
TZID:W. Europe
BEGIN:STANDARD
DTSTART:19701025T030000
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
TZNAME:W. Europe Standard Time
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19700329T020000
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
TZNAME:W. Europe Daylight Time
END:DAYLIGHT
END:VTIMEZONE

BEGIN:VTIMEZONE
TZID:US/Fictitious-Eastern
LAST-MODIFIED:19870101T000000Z
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4;UNTIL=20050403T070000Z
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
END:DAYLIGHT
END:VTIMEZONE

BEGIN:VTIMEZONE
TZID:America/Montreal
LAST-MODIFIED:20051013T233643Z
BEGIN:DAYLIGHT
DTSTART:20050403T070000
TZOFFSETTO:-0400
TZOFFSETFROM:+0000
TZNAME:EDT
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20051030T020000
TZOFFSETTO:-0500
TZOFFSETFROM:-0400
TZNAME:EST
END:STANDARD
END:VTIMEZONE

"""

__test__ = { "Test readOne" :
    r"""
    >>> silly = base.readOne(testSilly, findBegin=False)
    >>> silly
    <SILLYPROFILE| [<MORESTUFF{}this line is not folded, but in practice probably ought to be, as it is exceptionally long, and moreover demonstratively stupid>, <SILLYNAME{}name>, <STUFF{}foldedline>]>
    >>> silly.stuff
    <STUFF{}foldedline>
    >>> original = silly.serialize()
    >>> f3 = StringIO.StringIO(original.decode("utf-8"))
    >>> silly2 = base.readOne(f3)
    >>> silly2.serialize()==original
    True
    >>> s3 = StringIO.StringIO('cn:Babs Jensen\r\ncn:Barbara J Jensen\r\nsn:Jensen\r\nemail:babs@umich.edu\r\nphone:+1 313 747-4454\r\nx-id:1234567890\r\n')
    >>> ex1 = base.readOne(s3, findBegin=False)
    >>> ex1
    <*unnamed*| [<CN{}Babs Jensen>, <CN{}Barbara J Jensen>, <EMAIL{}babs@umich.edu>, <PHONE{}+1 313 747-4454>, <SN{}Jensen>, <X-ID{}1234567890>]>
    >>> ex1.serialize()
    'CN:Babs Jensen\r\nCN:Barbara J Jensen\r\nEMAIL:babs@umich.edu\r\nPHONE:+1 313 747-4454\r\nSN:Jensen\r\nX-ID:1234567890\r\n'
    """,
    
    "Import icaltest" :
    r"""
    >>> c = base.readOne(icaltest, validate=True)
    >>> c.vevent.valarm.trigger
    <TRIGGER{}-1 day, 0:00:00>
    >>> c.vevent.dtstart.value
    datetime.datetime(2002, 10, 28, 14, 0, tzinfo=<tzicalvtz 'US/Pacific'>)
    >>> c.vevent.dtend.value
    datetime.datetime(2002, 10, 28, 15, 0, tzinfo=<tzicalvtz 'US/Pacific'>)
    >>> c.vevent.dtstamp.value
    datetime.datetime(2002, 10, 28, 1, 17, 6, tzinfo=tzutc())
    >>> c.vevent.valarm.description.value
    u'Event reminder, with comma\nand line feed'
    >>> c.vevent.valarm.description.serialize()
    'DESCRIPTION:Event reminder\\, with comma\\nand line feed\r\n'
    >>> vevent = c.vevent.transformFromNative()
    >>> vevent.rrule
    <RRULE{}FREQ=Weekly;COUNT=10>
    """,
    
    "Parsing tests" :
    """
    >>> parseRDate = icalendar.MultiDateBehavior.transformToNative
    >>> icalendar.stringToTextValues('')
    ['']
    >>> icalendar.stringToTextValues('abcd,efgh')
    ['abcd', 'efgh']
    >>> icalendar.stringToPeriod("19970101T180000Z/19970102T070000Z")
    (datetime.datetime(1997, 1, 1, 18, 0, tzinfo=tzutc()), datetime.datetime(1997, 1, 2, 7, 0, tzinfo=tzutc()))
    >>> icalendar.stringToPeriod("19970101T180000Z/PT1H")
    (datetime.datetime(1997, 1, 1, 18, 0, tzinfo=tzutc()), datetime.timedelta(0, 3600))
    >>> parseRDate(base.textLineToContentLine("RDATE;VALUE=DATE:19970304,19970504,19970704,19970904"))
    <RDATE{'VALUE': ['DATE']}[datetime.date(1997, 3, 4), datetime.date(1997, 5, 4), datetime.date(1997, 7, 4), datetime.date(1997, 9, 4)]>
    >>> parseRDate(base.textLineToContentLine("RDATE;VALUE=PERIOD:19960403T020000Z/19960403T040000Z,19960404T010000Z/PT3H"))
    <RDATE{'VALUE': ['PERIOD']}[(datetime.datetime(1996, 4, 3, 2, 0, tzinfo=tzutc()), datetime.datetime(1996, 4, 3, 4, 0, tzinfo=tzutc())), (datetime.datetime(1996, 4, 4, 1, 0, tzinfo=tzutc()), datetime.timedelta(0, 10800))]>
    """,
    
    "read failure" :
    """
    >>> vevent = base.readOne(badstream)
    Traceback (most recent call last):
    ...
    ParseError: At line 11: TRIGGER with no VALUE not recognized as DURATION or as DATE-TIME
    >>> cal = base.readOne(badLineTest)
    Traceback (most recent call last):
    ...
    ParseError: At line 6: Failed to parse line: X-BAD/SLASH:TRUE
    >>> cal = base.readOne(badLineTest, ignoreUnreadable=True)
    >>> cal.vevent.x_bad_slash
    Traceback (most recent call last):
    ...
    AttributeError: x_bad_slash
    >>> cal.vevent.x_bad_underscore
    <X-BAD-UNDERSCORE{}TRUE>
    """,

    "ical trigger workaround" :
    """

    >>> badical = base.readOne(icalWeirdTrigger)
    >>> badical.vevent.valarm.description.value
    u'This trigger is a date-time without a VALUE=DATE-TIME parameter'
    >>> badical.vevent.valarm.trigger.value
    datetime.datetime(2002, 10, 28, 12, 0, tzinfo=tzutc())
    """,
    
    "unicode test" :
    r"""
    >>> f = resource_stream(__name__, 'test_files/utf8_test.ics')
    >>> vevent = base.readOne(f).vevent
    >>> vevent.summary.value
    u'The title \u3053\u3093\u306b\u3061\u306f\u30ad\u30c6\u30a3'
    >>> summary = vevent.summary.value
    >>> test = str(vevent.serialize()),
    """,
    
    # make sure date valued UNTILs in rrules are in a reasonable timezone,
    # and include that day (12/28 in this test)
    "recurrence test" :
    r"""
    >>> f = resource_stream(__name__, 'test_files/recurrence.ics')
    >>> cal = base.readOne(f)
    >>> dates = list(cal.vevent.rruleset)
    >>> dates[0]
    datetime.datetime(2006, 1, 26, 23, 0, tzinfo=tzutc())
    >>> dates[1]
    datetime.datetime(2006, 2, 23, 23, 0, tzinfo=tzutc())
    >>> dates[-1]
    datetime.datetime(2006, 12, 28, 23, 0, tzinfo=tzutc())
    """,
             
             
    "regular expression test" :
    """
    >>> re.findall(base.patterns['name'], '12foo-bar:yay')
    ['12foo-bar', 'yay']
    >>> re.findall(base.patterns['safe_char'], 'a;b"*,cd')
    ['a', 'b', '*', 'c', 'd']
    >>> re.findall(base.patterns['qsafe_char'], 'a;b"*,cd')
    ['a', ';', 'b', '*', ',', 'c', 'd']
    >>> re.findall(base.patterns['param_value'], '"quoted";not-quoted;start"after-illegal-quote', re.VERBOSE)
    ['"quoted"', '', 'not-quoted', '', 'start', '', 'after-illegal-quote', '']
    >>> match = base.line_re.match('TEST;ALTREP="http://www.wiz.org":value:;"')
    >>> match.group('value')
    'value:;"'
    >>> match.group('name')
    'TEST'
    >>> match.group('params')
    ';ALTREP="http://www.wiz.org"'
    """,
    
    "VTIMEZONE creation test:" :
        
    """
    >>> f = StringIO.StringIO(timezones)
    >>> tzs = dateutil.tz.tzical(f)
    >>> tzs.get("US/Pacific")
    <tzicalvtz 'US/Pacific'>
    >>> icalendar.TimezoneComponent(_)
    <VTIMEZONE | <TZID{}US/Pacific>>
    >>> pacific = _
    >>> print pacific.serialize()
    BEGIN:VTIMEZONE
    TZID:US/Pacific
    BEGIN:STANDARD
    DTSTART:20001029T020000
    RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
    TZNAME:PST
    TZOFFSETFROM:-0700
    TZOFFSETTO:-0800
    END:STANDARD
    BEGIN:DAYLIGHT
    DTSTART:20000402T020000
    RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
    TZNAME:PDT
    TZOFFSETFROM:-0800
    TZOFFSETTO:-0700
    END:DAYLIGHT
    END:VTIMEZONE
    >>> (_)
    <VTIMEZONE | <TZID{}US/Pacific>>
    >>> santiago = icalendar.TimezoneComponent(tzs.get('Santiago'))
    >>> ser = santiago.serialize()
    >>> print ser
    BEGIN:VTIMEZONE
    TZID:Santiago
    BEGIN:STANDARD
    DTSTART:20000311T000000
    RRULE:FREQ=YEARLY;BYDAY=2SA;BYMONTH=3
    TZNAME:Pacific SA Standard Time
    TZOFFSETFROM:-0300
    TZOFFSETTO:-0400
    END:STANDARD
    BEGIN:DAYLIGHT
    DTSTART:20001014T000000
    RRULE:FREQ=YEARLY;BYDAY=2SA;BYMONTH=10
    TZNAME:Pacific SA Daylight Time
    TZOFFSETFROM:-0400
    TZOFFSETTO:-0300
    END:DAYLIGHT
    END:VTIMEZONE
    >>> roundtrip = dateutil.tz.tzical(StringIO.StringIO(str(ser))).get()
    >>> for year in range(2001, 2010):
    ...     for month in (2, 9):
    ...         dt = datetime.datetime(year, month, 15, tzinfo = roundtrip)
    ...         if dt.replace(tzinfo=tzs.get('Santiago')) != dt:
    ...             print "Failed for:", dt
    >>> fict = icalendar.TimezoneComponent(tzs.get('US/Fictitious-Eastern'))
    >>> print fict.serialize()
    BEGIN:VTIMEZONE
    TZID:US/Fictitious-Eastern
    BEGIN:STANDARD
    DTSTART:20001029T020000
    RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
    TZNAME:EST
    TZOFFSETFROM:-0400
    TZOFFSETTO:-0500
    END:STANDARD
    BEGIN:DAYLIGHT
    DTSTART:20000402T020000
    RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4;UNTIL=20050403T070000Z
    TZNAME:EDT
    TZOFFSETFROM:-0500
    TZOFFSETTO:-0400
    END:DAYLIGHT
    END:VTIMEZONE
    """,

    "Create iCalendar from scratch" :
             
    """
    >>> cal = base.newFromBehavior('vcalendar', '2.0')
    >>> cal.add('vevent')
    <VEVENT| []>
    >>> cal.vevent.add('dtstart').value = datetime.datetime(2006, 5, 9)
    >>> cal.vevent.add('description').value = "Test event"
    >>> pacific = dateutil.tz.tzical(StringIO.StringIO(timezones)).get('US/Pacific')
    >>> cal.vevent.add('created').value = datetime.datetime(2006, 1, 1, 10, tzinfo=pacific)
    >>> cal.vevent.add('uid').value = "Not very random UID"
    >>> print cal.serialize()
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//PYVOBJECT//NONSGML Version 1//EN
    BEGIN:VEVENT
    UID:Not very random UID
    DTSTART:20060509T000000
    CREATED:20060101T180000Z
    DESCRIPTION:Test event
    END:VEVENT
    END:VCALENDAR
    """,

    "Serializing with timezones test" :
    
    """
    >>> from dateutil.rrule import rrule, rruleset, WEEKLY
    >>> pacific = dateutil.tz.tzical(StringIO.StringIO(timezones)).get('US/Pacific')
    >>> cal = base.Component('VCALENDAR')
    >>> cal.setBehavior(icalendar.VCalendar2_0)
    >>> ev = cal.add('vevent')
    >>> ev.add('dtstart').value = datetime.datetime(2005, 10, 12, 9, tzinfo = pacific)
    >>> set = rruleset()
    >>> set.rrule(rrule(WEEKLY, interval=2, byweekday=[2,4], until=datetime.datetime(2005, 12, 15, 9)))
    >>> set.exdate(datetime.datetime(2005, 10, 14, 9, tzinfo = pacific))
    >>> ev.rruleset = set
    >>> ev.add('uid').value = "uid could be generated but doctest complains"
    >>> ev.add('duration').value = datetime.timedelta(hours=1)
    >>> print cal.serialize()
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//PYVOBJECT//NONSGML Version 1//EN
    BEGIN:VTIMEZONE
    TZID:US/Pacific
    BEGIN:STANDARD
    DTSTART:20001029T020000
    RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
    TZNAME:PST
    TZOFFSETFROM:-0700
    TZOFFSETTO:-0800
    END:STANDARD
    BEGIN:DAYLIGHT
    DTSTART:20000402T020000
    RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
    TZNAME:PDT
    TZOFFSETFROM:-0800
    TZOFFSETTO:-0700
    END:DAYLIGHT
    END:VTIMEZONE
    BEGIN:VEVENT
    UID:uid could be generated but doctest complains
    DTSTART;TZID=US/Pacific:20051012T090000
    DURATION:PT1H
    EXDATE;TZID=US/Pacific:20051014T090000
    RRULE:FREQ=WEEKLY;BYDAY=WE,FR;INTERVAL=2;UNTIL=20051215T090000
    END:VEVENT
    END:VCALENDAR
    >>> apple = dateutil.tz.tzical(StringIO.StringIO(timezones)).get('America/Montreal')
    >>> ev.dtstart.value = datetime.datetime(2005, 10, 12, 9, tzinfo = apple)
    >>> print cal.serialize()
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//PYVOBJECT//NONSGML Version 1//EN
    BEGIN:VTIMEZONE
    TZID:US/Pacific
    BEGIN:STANDARD
    DTSTART:20001029T020000
    RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
    TZNAME:PST
    TZOFFSETFROM:-0700
    TZOFFSETTO:-0800
    END:STANDARD
    BEGIN:DAYLIGHT
    DTSTART:20000402T020000
    RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
    TZNAME:PDT
    TZOFFSETFROM:-0800
    TZOFFSETTO:-0700
    END:DAYLIGHT
    END:VTIMEZONE
    BEGIN:VTIMEZONE
    TZID:America/Montreal
    BEGIN:STANDARD
    DTSTART:20000101T000000
    RRULE:FREQ=YEARLY;BYMONTH=1;UNTIL=20040101T050000Z
    TZNAME:EST
    TZOFFSETFROM:-0500
    TZOFFSETTO:-0500
    END:STANDARD
    BEGIN:STANDARD
    DTSTART:20051030T020000
    RRULE:FREQ=YEARLY;BYDAY=5SU;BYMONTH=10
    TZNAME:EST
    TZOFFSETFROM:-0400
    TZOFFSETTO:-0500
    END:STANDARD
    BEGIN:DAYLIGHT
    DTSTART:20050403T070000
    RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4;UNTIL=20050403T120000Z
    TZNAME:EDT
    TZOFFSETFROM:-0500
    TZOFFSETTO:-0400
    END:DAYLIGHT
    END:VTIMEZONE
    BEGIN:VEVENT
    UID:uid could be generated but doctest complains
    DTSTART;TZID=America/Montreal:20051012T090000
    DURATION:PT1H
    EXDATE;TZID=US/Pacific:20051014T090000
    RRULE:FREQ=WEEKLY;BYDAY=WE,FR;INTERVAL=2;UNTIL=20051215T090000
    END:VEVENT
    END:VCALENDAR
    """,
    
    "Handling DATE without a VALUE=DATE" :
    
    """
    >>> cal = base.readOne(badDtStartTest)
    >>> cal.vevent.dtstart.value
    datetime.date(2002, 10, 28)
    """,

    "Serializing iCalendar to hCalendar" :
    
    """
    >>> cal = base.newFromBehavior('hcalendar')
    >>> cal.behavior
    <class 'vobject.hcalendar.HCalendar'>
    >>> pacific = dateutil.tz.tzical(StringIO.StringIO(timezones)).get('US/Pacific')
    >>> cal.add('vevent')
    <VEVENT| []>
    >>> cal.vevent.add('summary').value = "this is a note"
    >>> cal.vevent.add('url').value = "http://microformats.org/code/hcalendar/creator"
    >>> cal.vevent.add('dtstart').value = datetime.date(2006,2,27)
    >>> cal.vevent.add('location').value = "a place"
    >>> cal.vevent.add('dtend').value = datetime.date(2006,2,27) + datetime.timedelta(days = 2)
    >>> event2 = cal.add('vevent')
    >>> event2.add('summary').value = "Another one"
    >>> event2.add('description').value = "The greatest thing ever!"
    >>> event2.add('dtstart').value = datetime.datetime(1998, 12, 17, 16, 42, tzinfo = pacific)
    >>> event2.add('location').value = "somewhere else"
    >>> event2.add('dtend').value = event2.dtstart.value + datetime.timedelta(days = 6)
    >>> hcal = cal.serialize()
    >>> print hcal
    <span class="vevent">
       <a class="url" href="http://microformats.org/code/hcalendar/creator">
          <span class="summary">this is a note</span>:
          <abbr class="dtstart", title="20060227">Monday, February 27</abbr>
          - <abbr class="dtend", title="20060301">Tuesday, February 28</abbr>
          at <span class="location">a place</span>
       </a>
    </span>
    <span class="vevent">
       <span class="summary">Another one</span>:
       <abbr class="dtstart", title="19981217T164200-0800">Thursday, December 17, 16:42</abbr>
       - <abbr class="dtend", title="19981223T164200-0800">Wednesday, December 23, 16:42</abbr>
       at <span class="location">somewhere else</span>
       <div class="description">The greatest thing ever!</div>
    </span>
    """,

    "Generate UIDs automatically test:" :
             
    """
    >>> cal = base.newFromBehavior('vcalendar')
    >>> cal.add('vevent').add('dtstart').value = datetime.datetime(2006,2,2,10)
    >>> ser = cal.serialize()
    >>> len(cal.vevent.uid_list)
    1
    """,

    "VCARD 3.0 parse test:" :
        
    r"""
    >>> card = base.readOne(vcardtest)
    >>> card.adr.value
    <Address: Haight Street 512;\nEscape, Test\nNovosibirsk,  80214\nGnuland>
    >>> print card.adr.value
    Haight Street 512;
    Escape, Test
    Novosibirsk,  80214
    Gnuland
    >>> card.org.value
    [u'University of Novosibirsk, Department of Octopus Parthenogenesis']
    >>> print card.serialize()
    BEGIN:VCARD
    VERSION:3.0
    ACCOUNT;TYPE=HOME:010-1234567-05
    ADR;TYPE=HOME:;;Haight Street 512\;\nEscape\, Test;Novosibirsk;;80214;Gnul
     and
    BDAY;VALUE=date:02-10
    FN:Daffy Duck Knudson (with Bugs Bunny and Mr. Pluto)
    N:Knudson;Daffy Duck (with Bugs Bunny and Mr. Pluto);;;
    NICKNAME:gnat and gnu and pluto
    ORG:University of Novosibirsk\, Department of Octopus Parthenogenesis
    TEL;TYPE=HOME:+01-(0)2-765.43.21
    TEL;TYPE=CELL:+01-(0)5-555.55.55
    TEL;TYPE=HOME:+01-(0)2-876.54.32
    END:VCARD
    """,
             
    "Multi-text serialization test:" :
             
    """
    >>> category = base.newFromBehavior('categories')
    >>> category.value = ['Random category']
    >>> print category.serialize().strip()
    CATEGORIES:Random category
    >>> category.value.append('Other category')
    >>> print category.serialize().strip()
    CATEGORIES:Random category,Other category
    """,
             
    "vCard groups test:" :
             
    """
    >>> card = base.readOne(vcardWithGroups)
    >>> card.group
    u'home'
    >>> card.tel.group
    u'home'
    >>> card.group = card.tel.group = 'new'
    >>> card.tel.serialize().strip()
    'new.TEL;TYPE=fax,voice,msg:+49 3581 123456'
    >>> card.serialize().splitlines()[0]
    'new.BEGIN:VCARD'
    >>> dtstart = base.newFromBehavior('dtstart')
    >>> dtstart.group = "badgroup"
    >>> dtstart.serialize()
    Traceback (most recent call last):
    ...
    VObjectError: "<DTSTART{}> has a group, but this object doesn't support groups"
    """,

    "Lowercase components test:" :
             
    """
    >>> card = base.readOne(lowercaseComponentNames)
    >>> card.version
    <VERSION{}2.1>
    """,

    "Default behavior test" :
             
    """
    >>> card = base.readOne(vcardWithGroups)
    >>> base.getBehavior('note') == None
    True
    >>> card.note.behavior
    <class 'vobject.vcard.VCardTextBehavior'>
    >>> print card.note.value
    The Mayor of the great city of  Goerlitz in the great country of Germany.
    Next line.
    """
    }
