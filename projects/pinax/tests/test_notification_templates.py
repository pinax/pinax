from notification.models import NoticeType, get_formatted_messages

FORMATS = [
    'short.txt',
    'plain.txt',
    'teaser.html',
    'full.html',
]

class MockDict:
    def __contains__(self, key):
        return True
    
    def __getitem__(self, key):
        return "[%s]" % key
    
    def __setitem__(self, key, value):
        pass

MOCK_CONTEXT = MockDict()

def run():

    for notice_type in NoticeType.objects.all():
        label = notice_type.label
        print "-" * 72
        print "testing %s..." % label
        messages = get_formatted_messages(FORMATS, label, MOCK_CONTEXT)
        for format in FORMATS:
            print "%s:" % format
            print messages[format.split(".")[0]]
        print
    