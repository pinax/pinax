from django.conf.urls.defaults import *

from blog import views, models
from blog.forms import *


urlpatterns = patterns('',
    # blog post
    url(r'^post/(?P<username>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[-\w]+)/$', 'blog.views.post', name='blog_post'),

    # all blog posts
    url(r'^$', 'blog.views.blogs', name="blog_list_all"),

    # blog post for user
    url(r'^posts/(?P<username>\w+)/$', 'blog.views.blogs', name='blog_list_user'),

    # your posts
    url(r'^your_posts/$', 'blog.views.your_posts', name='blog_list_yours'),

    # new blog post
    url(r'^new/$', 'blog.views.new', name='blog_new'),

    # edit blog post
    url(r'^edit/(\d+)/$', 'blog.views.edit', name='blog_edit'),

    #destory blog post
    url(r'^destroy/(\d+)/$', 'blog.views.destroy', name='blog_destroy'),

    # ajax validation
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': BlogForm, 'callback': lambda request, *args, **kwargs: {'user': request.user}}, 'blog_form_validate'),
)
