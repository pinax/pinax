# Quick Start

Make sure you've read [What is Pinax?](what_is_pinax.md) to get a conceptual overview of Pinax.

We strongly recommend running Pinax (or indeed, any Django) projects in a virtual environment:

```
pip install virtualenv
virtualenv mysiteenv
source mysiteenv/bin/activate
```

Once your virtual environment has been activated, install Django and use `django-admin` to create a new project based on the Account Pinax starter project:

```
pip install Django==1.8.4
django-admin startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/account mysite -n webpack.config.js
```

Now install the requirements, initialize your database, load the default sites fixtures and run the dev server:

```
cd mysite
pip install -r requirements.txt
chmod +x manage.py
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```

You now have a running Django site complete with account management and bootstrap-based templates.


@@@ Then add one more app
