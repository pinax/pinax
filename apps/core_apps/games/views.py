from arcade.models import Game, ArcadeCategory

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

def game_detail(request, slug='', template_name='games/game_detail.html'):
    game = get_object_or_404(Game, slug=slug.lower())
    if request.META.get('HTTP_REFERER', '') != request.path:
        game.add_play()
    return render_to_response(template_name, {
        'game': game,
    }, context_instance=RequestContext(request))
