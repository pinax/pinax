from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# from django.contrib.auth.models import User

from zwitschern.models import Tweet, TweetInstance, tweet

@login_required
def personal(request):
    """
    just the tweets the current user is following
    """
    if request.method == "POST":
        if request.POST["action"] == "post":
            text = request.POST["tweet"].strip()
            tweet(request.user, text)
        reply = None
    else:
        reply = request.GET.get("reply")
            
    tweets = TweetInstance.objects.filter(recipient=request.user).order_by("-sent")
    
    return render_to_response("zwitschern/personal.html", {
        "reply": reply,
        "tweets": tweets,
    }, context_instance=RequestContext(request))

def public(request, threshold=10):
    """
    the latest tweets limited by the threshold
    """
    tweets = Tweet.objects.all().order_by("-sent")[:threshold]

    return render_to_response("zwitschern/public.html", {
        "tweets": tweets,
        "threshold": threshold,
    }, context_instance=RequestContext(request))

def single(request, id):
    """
    A single tweet.
    """
    tweet = get_object_or_404(TweetInstance, id=id)
    return render_to_response("zwitschern/single.html", {
        "tweet": tweet,
    }, context_instance=RequestContext(request))