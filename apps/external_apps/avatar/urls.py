from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('avatar',
    url('^change/$', 'views.change', name='avatar_change'),
    url('^delete/$', 'views.delete', name='avatar_delete'),
    url('^(\w+)/$', 'views.img', name='avatar_img'),
)
