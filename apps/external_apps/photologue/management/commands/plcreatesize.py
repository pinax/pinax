from django.core.management.base import BaseCommand, CommandError
from photologue.management.commands import create_photosize

class Command(BaseCommand):
    help = ('Creates a new Photologue photo size interactively.')
    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        create_size(args[0])

def create_size(size):
    create_photosize(size)
