# Quick Start

Make sure you've read [What is Pinax?](what_is_pinax.md) to get a conceptual overview of Pinax.

We strongly recommend running Pinax (or indeed, any Django) projects in a virtual environment:

```shell
pip install virtualenv
virtualenv mysiteenv
source mysiteenv/bin/activate
pip install pinax-cli
pinax start account mysite
```

If you are using `pipenv` try this instead:

```shell
mkdir mysite
cd mysite
pipenv --three
pipenv shell
pip install pinax-cli
pinax start account mysite --location .
```

**NOTE**: _If you are wondering what `pinax start` actually does, it is equivalent to:_

```shell
pip install Django==2.0
django-admin startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/account mysite
```

Now install the requirements, initialize your database, load the default sites fixtures, and run the dev server:

```shell
cd mysite
pip install -r requirements.txt
chmod +x manage.py
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```

You now have a running Django site complete with account management and bootstrap-based templates.


## Adding Another Pinax App

Add the new app name to `requirements.txt`:

```python
    # other apps
    pinax-amazing==2.0.1,
```

and install requirements once again.

```shell
pip install -r requirements.txt
```

If you are using `pipenv`, you know to use this instead:

```python
pipenv install pinax-amazing==2.0.1
```

Next, modify `settings.py` by adding your app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # other apps
    "pinax-amazing",
]
```

This is a good time to make any additional changes to `settings.py` if needed for the new app.

Be sure to establish database tables for the new app:

```shell
./manage.py migrate
```

Finally, modify your project `urls.py` with urls for the new app:

```
    urlpatterns = [
        # other urls
        url(r"^amazing/", include("pinax.amazing.urls", namespace="pinax_amazing")),
    ]
```

This is a good time to adjustment templates for the new app, if needed.
