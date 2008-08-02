from django.conf.urls.defaults import *

urlpatterns = patterns('games',
    url(r'^game/(?P<slug>[a-zA-Z0-9_-]+)/$', 'views.game_detail', name='games_detail'),
    url(r'^$', 'views.game_list', name='games_index'),
)