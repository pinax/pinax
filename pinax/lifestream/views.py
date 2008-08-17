
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import datetime

import twitter
import pownce
import random
import zlib
import base64
from zwitschern.utils import twitter_account_for_user, twitter_verify_credentials
from zwitschern.pownce_utils import pownce_account_for_user, pownce_verify_credentials
from settings import SECRET_KEY

# from django.contrib.auth.models import User

from zwitschern.models import Tweet, TweetInstance, tweet

@login_required
def personal(request):
    """
    personal lifestream
    """
    
    stream = []
    
    twitter_account = twitter_account_for_user(request.user)
    if twitter_account:
        twitter_timeline = twitter_account.GetUserTimeline()
        for post in twitter_timeline:
            stream.append((post.created_at, post.GetText(), post.id))
            
    pownce_account  = pownce_account_for_user(request.user)
    if pownce_account:
        pownce_timeline = pownce_account.get_notes(pownce_account.username)
        for post in pownce_timeline:
            stream.append(( post.timestamp_parsed,post.body, post.id))
    
    stream.sort()
    if request.method == "POST":
        pass
    else:
        pass
    
    return render_to_response("lifestream/personal.html", {
        "stream": stream,
    }, context_instance=RequestContext(request))

def public(request):
    """
    all the tweets
    """
    tweets = Tweet.objects.all().order_by("-sent")

    return render_to_response("lifestream/friends.html", {
        "tweets": tweets,
    }, context_instance=RequestContext(request))

def single(request, id):
    """
    A single tweet.
    """
    tweet = get_object_or_404(TweetInstance, id=id)
    return render_to_response("lifestream/single.html", {
        "tweet": tweet,
    }, context_instance=RequestContext(request))