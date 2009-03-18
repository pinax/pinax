from app_plugins import Library

register = Library()

@register.plugin_point(takes_context=True, takes_user=True, takes_args=True)
def profile(point, context, user, owner, viewer):
    """
    """
    return {'is_owner': owner == viewer }
