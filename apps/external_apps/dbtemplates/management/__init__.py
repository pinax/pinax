from django.db.models import signals
from django.contrib.sites.models import Site

from dbtemplates.models import Template
from dbtemplates import models as template_app

def create_default_templates(app, created_models, verbosity, **kwargs):
    """Creates the default database template objects."""
    try:
        site = Site.objects.get_current()
    except Site.DoesNotExist:
        site = None

    if site is not None:
        if Template in created_models:
            if verbosity >= 2:
                print "Creating default database templates for error 404 and 500"

            template404, created404 = Template.objects.get_or_create(
                name="404.html")
            if created404:
                template404.content="""
{% extends "base.html" %}
{% load i18n %}
{% block content %}
    <h2>{% trans 'Page not found' %}</h2>
    <p>{% trans "We're sorry, but the requested page could not be found." %}</p>
{% endblock %}
"""
                template404.save()
                template404.sites.add(site)

            template500, created500 = Template.objects.get_or_create(
                name="500.html")
            if created500:
                template500.content="""
{% extends "base.html" %}
{% load i18n %}
{% block content %}
    <h1>{% trans 'Server Error <em>(500)</em>' %}</h1>
    <p>{% trans "There's been an error." %}</p>
{% endblock %}
"""
                template500.save()
                template500.sites.add(site)

signals.post_syncdb.connect(create_default_templates, sender=template_app)
