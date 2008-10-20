# -*- coding: utf-8 -*-

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'dev.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'US/Eastern'
LANGUAGE_CODE = 'en'

SITE_ID = 1

USE_I18N = True

import os.path

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "site_media")
MEDIA_URL = '/site_media/'
ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = 'bk-e2zv3humar79nm=j*bwc=-ymeit(8a20whp3goq4dh71t)s'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openidconsumer.middleware.OpenIDMiddleware',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'basic_project.urls'

import os.path

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "account.context_processors.openid",
    "account.context_processors.account",
    "misc.context_processors.contact_email",
    # "misc.context_processors.site_name",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    
    # external
    'notification', # must be first
    'emailconfirmation',
    'mailer',
    'announcements',
    'django_openidconsumer',
    'django_openidauth',
    'pagination',
    'timezones',
    'ajax_validation',
    
    # internal (for now)
    'basic_profiles',
    'account',
    'misc',
    
    'django.contrib.admin',

)

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/%s/" % o.username,
}

AUTH_PROFILE_MODULE = 'basic_profiles.Profile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "feedback@example.com"
# SITE_NAME = "Pinax"
LOGIN_URL = "/account/login"

try:
    from localsettings import *
except ImportError:
    pass
