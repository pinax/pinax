from django.conf.urls.defaults import *

from blog import views, models
from blog.forms import *


urlpatterns = patterns('',
    # blog post
    url(r'^post/(?P<username>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[-\w]+)/$', 'blog.views.post', name='post'),
    
    # all blog posts
    url(r'^$', 'blog.views.blogs'),
    
    # your posts
    url(r'^your_posts/$', 'blog.views.your_posts', name="your_posts"),
    
    # new blog post
    url(r'^new/$', 'blog.views.new'),
    
    # edit blog post
    url(r'^edit/(\d+)/$', 'blog.views.edit', name="edit_post"),

    # ajax validation
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': BlogForm}, 'blog_form_validate'),
)
