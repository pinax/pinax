
from djopenid import util
from django.views.generic.simple import direct_to_template

def index(request):
    consumer_url = util.getViewURL(
        request, 'djopenid.consumer.views.startOpenID')
    server_url = util.getViewURL(request, 'djopenid.server.views.server')

    return direct_to_template(
        request,
        'index.html',
        {'consumer_url':consumer_url, 'server_url':server_url})

