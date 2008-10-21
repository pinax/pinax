from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from photologue.models import PhotoSize, ImageModel

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--reset', '-r', action='store_true', dest='reset', help='Reset photo cache before generating'),
    )

    help = ('Manages Photologue cache file for the given sizes.')
    args = '[sizes]'

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        return create_cache(args, options)

def create_cache(sizes, options):
    """
    Creates the cache for the given files
    """
    reset = options.get('reset', None)

    size_list = [size.strip(' ,') for size in sizes]

    if len(size_list) < 1:
        sizes = PhotoSize.objects.filter(pre_cache=True)
    else:
        sizes = PhotoSize.objects.filter(name__in=size_list)

    if not len(sizes):
        raise CommandError('No photo sizes were found.')

    print 'Caching photos, this may take a while...'

    for cls in ImageModel.__subclasses__():
        for photosize in sizes:
            print 'Cacheing %s size images' % photosize.name
            for obj in cls.objects.all():
                if reset:
                    obj.remove_size(photosize)
                obj.create_size(photosize)
