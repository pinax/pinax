from django.template import Library

register = Library()

@register.inclusion_tag("blog/blog_item.html")
def show_blog_post(blog_post):
    return {"blog_post": blog_post}
