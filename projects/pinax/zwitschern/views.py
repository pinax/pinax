
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

import twitter
import random
import zlib
import base64
from zwitschern.utils import twitter_account_for_user, twitter_verify_credentials
from settings import SECRET_KEY

# from django.contrib.auth.models import User

from zwitschern.models import Tweet, TweetInstance, tweet

@login_required
def personal(request):
    """
    just the tweets the current user is following
    """
    twitter_account = twitter_account_for_user(request.user)
    
    if request.method == "POST":
        if request.POST["action"] == "post":
            text = request.POST["tweet"].strip()
            tweet(request.user, text)
            if request.POST.get('pub2twitter', '') == "yes":
                twitter_account.PostUpdate(text)
        reply = None
    else:
        reply = request.GET.get("reply")
    
    tweets = TweetInstance.objects.tweets_for(request.user).order_by("-sent")
    twitter_authorized = twitter_verify_credentials(twitter_account)
    
    return render_to_response("zwitschern/personal.html", {
        "reply": reply,
        "tweets": tweets,
        "twitter_authorized": twitter_authorized,
    }, context_instance=RequestContext(request))

def public(request):
    """
    all the tweets
    """
    tweets = Tweet.objects.all().order_by("-sent")

    return render_to_response("zwitschern/public.html", {
        "tweets": tweets,
    }, context_instance=RequestContext(request))

def single(request, id):
    """
    A single tweet.
    """
    tweet = get_object_or_404(TweetInstance, id=id)
    return render_to_response("zwitschern/single.html", {
        "tweet": tweet,
    }, context_instance=RequestContext(request))