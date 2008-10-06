import things
from arcade.models import ArcadeCategory, Game

class GameThing(things.Thing):
    game_plays = things.OrderField(
        verbose_name_asc='Play Count',
        verbose_name_desc='Play Count',
        url_asc='most-played',
        url_desc='least-played'
    )
    created = things.OrderField(
        verbose_name_asc='Date Added',
        verbose_name_desc='Date Added',
        url_asc='newest',
        url_desc='oldest'
    )
    name = things.OrderField(
        verbose_name_asc='Alphabetical',
        verbose_name_desc='Alphabetical',
    )
    template_dir = 'games'
    

class GameThingGroup(things.ThingGroup):
    template_dir = 'games'
    template_name = 'category_list.html'

def group_dicts(thing):
    dicts = [
        {
            'queryset': Game.objects.all(),
            'name': 'All',
            'url_name': 'all',
        },
    ]
    for category in ArcadeCategory.objects.all():
        dicts.append({
            'queryset': category.game_set.all(),
            'name': category.name,
            'url_name': category.slug,
        })
    return dicts