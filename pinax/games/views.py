from arcade.models import Game

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

def game_list(request):
    context = {
        'games': Game.objects.filter(downloaded=True),
    }
    return render_to_response('games/game_list.html',
        context, context_instance=RequestContext(request))

def game_detail(request, slug=''):
    context = {
        'game': get_object_or_404(Game, slug=slug.lower()),
    }
    return render_to_response('games/game_detail.html',
        context, context_instance=RequestContext(request))