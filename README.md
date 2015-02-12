# pinax

[![Join the chat at https://gitter.im/pinax/pinax](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/pinax/pinax?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Pinax is an ecosystem of reusable Django apps, themes, and starter project
templates.

This collection can be found at [http://pinaxproject.com](http://pinaxproject.com).

To give you an example of how one would use Pinax now to start a new
site based on the [Account Starter Project](https://github.com/pinax/pinax-project-account) follow these steps in your shell:

```
pip install virtualenv
virtualenv mysiteenv
source mysiteenv/bin/activate
pip install Django==1.7.4
django-admin.py startproject --template=https://github.com/pinax/pinax-project-account/zipball/master mysite
cd mysite
pip install -r requirements.txt
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```
