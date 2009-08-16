import os
from django.core.management.base import LabelCommand
from staticfiles.utils import get_media_path

class Command(LabelCommand):
    help = "Finds the location of the given media by resolving its path."
    args = "[media_path]"
    label = 'media path'

    def handle_label(self, media_path, **options):
        print "Resolving %s:" % media_path
        paths = get_media_path(media_path, all=True)
        if paths is None:
            print "  No media found."
        else:
            for path in paths:
                print u"  %s" % os.path.realpath(path)
