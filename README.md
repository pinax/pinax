# Pinax

[![Join us on Slack](http://slack.pinaxproject.com/badge.svg)](http://slack.pinaxproject.com/)

Pinax is an open-source platform built on the Django Web Framework. It is an ecosystem of reusable Django apps, themes, and starter project templates.
This collection can be found at http://pinaxproject.com.

In order to foster a kind, inclusive, and harassment-free community, the Pinax Project has a code of conduct, which can be found here  http://pinaxproject.com/pinax/code_of_conduct/.

The Pinax documentation is available at http://pinaxproject.com/pinax/.

For updates and news regarding the Pinax Project, please follow us on Twitter at [@pinaxproject](https://twitter.com/pinaxproject) and check out our blog http://blog.pinaxproject.com.

To give you an example of how one would use Pinax now to start a new
site based on the [Account Starter Project](https://github.com/pinax/pinax-project-account) follow these steps in your shell:

```
pip install virtualenv
virtualenv mysiteenv
source mysiteenv/bin/activate
pip install Django==1.8.3
django-admin.py startproject --template=https://github.com/pinax/pinax-project-account/zipball/master mysite
cd mysite
pip install -r requirements.txt
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```
