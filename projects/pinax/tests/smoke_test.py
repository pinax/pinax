## initially a quick smoke test to see if certain URLs throw exceptions or not
## would have caught a high percentage of recent trunk breakages 

## run with ./manage.py runscript tests.smoke_test

def run():
    from django.test.client import Client
    c = Client()
    
    pages = [
        '/',
        '/apps/',
        '/sites/',
        '/team/',
        '/about/',
        '/profiles/',
        '/blog/',
        '/invitations/',
        '/notices/',
        '/messages/',
        '/announcements/',
        '/tweets/',
        '/tribes/',
        '/projects/',
        '/robots.txt',
        '/photos/',
        '/bookmarks/',
    ]
    
    for page in pages:
        print page, 
        try:
            print c.get(page).status_code
        except Exception, e:
            print e
