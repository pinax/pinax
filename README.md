# pinax

Pinax has always been about a larger ecosystem of reusable apps. Now that
Django supports the notion of project templates, there is no longer a
need for Pinax's version of the infrastructure to support what we call
the starter project.

Pinax is an ecosystem of reusable Django apps, themes, and starter project
templates.

This collection can be found at [http://pinax.github.com](http://pinax.github.com).

To give you an example of how one would use Pinax now to start a new
site based on the [Account Starter Project](https://github.com/pinax/pinax-project-account) follow these steps in your shell:

    $ mkvirtualenv mysite
    $ pip install Django==1.4.5
    $ django-admin.py startproject --template=https://github.com/pinax/pinax-project-account/zipball/master mysite
    $ cd mysite
    $ pip install -r requirements.txt
    $ python manage.py syncdb
    $ python manage.py runserver
