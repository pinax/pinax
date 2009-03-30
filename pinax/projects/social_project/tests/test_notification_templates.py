from notification.models import NoticeType, get_formatted_messages

FORMATS = [
    'short.txt',
    'full.txt',
    'notice.html',
    'full.html',
]

class MockDict:
    def __contains__(self, key):
        return True
    
    def __getitem__(self, key):
        return "{{%s}}" % key
    
    def __setitem__(self, key, value):
        pass
    
    def update(self, e, **f):
        pass
        
    def pop(self):
        pass

MOCK_CONTEXT = MockDict()

def run():

    for notice_type in NoticeType.objects.all():
        label = notice_type.label
        print "-" * 72
        print "testing %s..." % label
        try:
            messages = get_formatted_messages(FORMATS, label, MOCK_CONTEXT)
        except Exception, e:
            print e
        for format in FORMATS:
            print "%s:" % format
            print messages[format]
        print
    