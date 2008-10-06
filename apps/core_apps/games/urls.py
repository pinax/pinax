import things
from django.conf.urls.defaults import *
from games.thing import GameThing, GameThingGroup, group_dicts

thing = GameThingGroup(GameThing, group_func=group_dicts)

urlpatterns = thing.urls(name_prefix='games') + patterns('games',
    url(
        r'^game/(?P<slug>[a-zA-Z0-9_-]+)/$', 
        'views.game_detail',
        {'extra_context': {'groups': thing.groups}},
        name='game_detail'),
)