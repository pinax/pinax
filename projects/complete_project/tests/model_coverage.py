from django.db.models.loading import get_models, get_apps

def run():
    for app_mod in get_apps():
        app_models = get_models(app_mod)
        for model in app_models:
            try:
                print model.__module__, model.__name__, model.objects.all().count()
            except Exception, e:
                print e
