from django.conf.urls.defaults import *

from blog import views, models
from blog.forms import *


urlpatterns = patterns('',
    # blog post
    url(r'^article/(?P<username>[-\w]+)/(?P<year>\d{1})/(?P<month>\d{4})/(?P<slug>[-\w]+)/$', 'blog.views.article', name='article'),
    
    # all blog posts
    url(r'^$', 'blog.views.blogs'),
    
    # your articles
    url(r'^yourarticles/$', 'blog.views.yourarticles', name="your_articles"),
    
    # new blog post
    url(r'^new/$', 'blog.views.new'),
    
    # edit blog post
    url(r'^edit/(\d+)/$', 'blog.views.edit', name="edit_post"),

    # ajax validation
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': BlogForm}, 'blog_form_validate'),
)
