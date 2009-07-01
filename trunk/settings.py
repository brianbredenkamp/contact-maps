# -*- coding: utf-8 -*-
from ragendja.settings_pre import *

MEDIA_URL = '/media/'

# Increase this when you update your media on the production site, so users
# don't have to refresh their cache. By setting this your MEDIA_URL
# automatically becomes /media/MEDIA_VERSION/
MEDIA_VERSION = 1

# Change your email settings
if on_production_server:
    DEFAULT_FROM_EMAIL = 'contactmaps@yourdomain.com'
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0123456789' # This is the default from app-engine-patch! Change it!

# Enable I18N and set default language to 'en'
USE_I18N = False
LANGUAGE_CODE = 'en'

# Restrict supported languages
ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'contactmaps.context_processors.contactmaps_settings',
)

MIDDLEWARE_CLASSES = (
    'ragendja.middleware.ErrorMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # Google authentication
    'ragendja.auth.middleware.GoogleAuthenticationMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

# Google authentication
AUTH_USER_MODULE = 'ragendja.auth.google_models'
AUTH_ADMIN_MODULE = 'ragendja.auth.google_admin'

LOGIN_URL = '/login/'
LOGOUT_URL = '/account/logout/'
LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sites',
    'appenginepatcher',
    'contactmaps',
)

DATABASE_OPTIONS = {}

from ragendja.settings_post import *
