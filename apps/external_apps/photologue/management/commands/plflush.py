from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from photologue.models import PhotoSize, ImageModel

class Command(BaseCommand):
    help = ('Clears the Photologue cache for the given sizes.')
    args = '[sizes]'

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        return create_cache(args, options)

def create_cache(sizes, options):
    """
    Clears the cache for the given files
    """
    size_list = [size.strip(' ,') for size in sizes]

    if len(size_list) < 1:
        sizes = PhotoSize.objects.all()
    else:
        sizes = PhotoSize.objects.filter(name__in=size_list)

    if not len(sizes):
        raise CommandError('No photo sizes were found.')

    print 'Flushing cache...'

    for cls in ImageModel.__subclasses__():
        for photosize in sizes:
            print 'Flushing %s size images' % photosize.name
            for obj in cls.objects.all():
                obj.remove_size(photosize)
