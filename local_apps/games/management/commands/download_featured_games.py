from django.core.management.base import NoArgsCommand
from arcade.models import Game
from arcade.scripts.process_queue import ProcessDownloadQueue

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        featured_games_to_download = Game.objects.filter(featured=True, downloaded=False)
        for game in featured_games_to_download:
            print "Processing %s" % game.name
            ProcessDownloadQueue(game).run()
        print "Finished downloading featured games."