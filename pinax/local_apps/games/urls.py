from django.conf.urls.defaults import *

urlpatterns = patterns('games',
    url(r'^game/(?P<slug>[a-zA-Z0-9_-]+)/$', 'views.game_detail', name='games_detail'),
    url(r'^category/(?P<category>[a-zA-Z0-9_-]+)/$', 'views.game_list', name='games_category'),
    url(r'^category/(?P<category>[a-zA-Z0-9_-]+)/(?P<sort>[a-z-]+)/$', 'views.game_list', name='games_category_list'),
    url(r'^categories/$', 'views.categories', name='games_categories'),
    url(r'^(?P<sort>[a-z-]+)/$', 'views.game_list', name='games_list'),
    url(r'^$', 'views.game_list', name='games_index'),
)