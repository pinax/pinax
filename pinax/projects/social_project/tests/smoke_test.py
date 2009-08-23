## initially a quick smoke test to see if certain URLs throw exceptions or not
## would have caught a high percentage of recent trunk breakages

## run with ./manage.py runscript tests.smoke_test

def run():
    from django.test.client import Client
    c = Client()
    
    pages = [
        '/',
        '/about/',
        '/profiles/',
        '/blog/',
        '/invitations/',
        '/notices/',
        '/messages/',
        '/announcements/',
        '/tweets/',
        '/tribes/',
        '/robots.txt',
        '/photos/',
        '/bookmarks/',
    ]
    
    for page in pages:
        print page,
        try:
            x = c.get(page)
            if x.status_code in [301, 302]:
                print x.status_code, "=>", x["Location"]
            else:
                print x.status_code
                
        except Exception, e:
            print e
