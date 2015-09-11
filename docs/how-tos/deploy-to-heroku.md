# Deploying to Heroku

This document assumes you have followed our [Quick Start](../quick_start.md) guide.

First, create a Heroku app:

```bash
heroku create
```

Set the buildpack for the app to use Python:

```bash
heroku buildpacks:set git://github.com/heroku/heroku-buildpack-python.git
```

Setting the buildpack explicitly is required due to the buildpack detection ordering.
Our projects include a `package.json` file which will trick Heroku in thinking
your project is a Node.js app. It should identify it as a Python app.

## Setting up your project

In your project add the following to your `requirements.txt`:

    django-toolbelt

Create a file named `Procfile` in your project with the following content:

    web: gunicorn --log-file - mysite.wsgi

In your `settings.py` change:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "dev.db",
        }
    }

to:

    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config()
    }

In your `mysite/wsgi.py` change:

    application = get_wsgi_application()

to:

    from dj_static import Cling, MediaCling
    application = Cling(MediaCling(get_wsgi_application()))

## Commit to git

Add everything to git and commit:

```bash
git add .
git commit -m "added Heroku support"
```

## Deploy to Heroku

To deploy to Heroku you use `git`:

```bash
git push heroku master
```

Run migrations:

```bash
heroku run python manage.py migrate
```
