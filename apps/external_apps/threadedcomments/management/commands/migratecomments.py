from django.core.management.base import BaseCommand
from django.contrib.comments.models import Comment, FreeComment
from threadedcomments.models import ThreadedComment, FreeThreadedComment

class Command(BaseCommand):
    help = "Migrates Django's built-in django.contrib.comments data to threadedcomments data"
    
    output_transaction = True
    
    def handle(self, *args, **options):
        """
        Converts all legacy ``Comment`` and ``FreeComment`` objects into 
        ``ThreadedComment`` and ``FreeThreadedComment`` objects, respectively.
        """
        self.handle_free_comments()
        self.handle_comments()
    
    def handle_free_comments(self):
        """
        Converts all legacy ``FreeComment`` objects into ``FreeThreadedComment``
        objects.
        """
        comments = FreeComment.objects.all()
        for c in comments:
            new = FreeThreadedComment(
                content_type = c.content_type,
                object_id = c.object_id,
                comment = c.comment,
                name = c.person_name,
                website = '',
                email = '',
                date_submitted = c.submit_date,
                date_modified = c.submit_date,
                date_approved = c.submit_date,
                is_public = c.is_public,
                ip_address = c.ip_address,
                is_approved = c.approved
            )
            new.save()
    
    def handle_comments(self):
        """
        Converts all legacy ``Comment`` objects into ``ThreadedComment`` objects.
        """
        comments = Comment.objects.all()
        for c in comments:
            new = ThreadedComment(
                content_type = c.content_type,
                object_id = c.object_id,
                comment = c.comment,
                user = c.user,
                date_submitted = c.submit_date,
                date_modified = c.submit_date,
                date_approved = c.submit_date,
                is_public = c.is_public,
                ip_address = c.ip_address,
                is_approved = not c.is_removed
            )
            new.save()