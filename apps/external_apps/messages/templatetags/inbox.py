from django.template import Library, Node

class InboxOutput(Node):
    def render(self, context):
        user = context['user']
        count = user.received_messages.filter(read_at__isnull=True, recipient_deleted_at__isnull=True).count()
        return "%s" % (count)        
        
def do_print_inbox_count(parser, token):
    """
    A templatetag to show the unread-count for a logged in user.
    Prints the number of unread messages in the user's inbox.
    Usage::
        {% load inbox %}
        {% inbox_count %}
     
    """
    return InboxOutput()

register = Library()     
register.tag('inbox_count', do_print_inbox_count)