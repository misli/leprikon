# -*- coding: utf-8 -*-
"""
Django settings for leprikon.site project.

Generated by 'django-admin startproject' using Django 1.10.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.environ.get('BASE_DIR', os.getcwd())
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(BASE_DIR, 'data'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', os.environ.get('DEBUG'))
if not SECRET_KEY:
    from django.utils.crypto import get_random_string
    SECRET_KEY = get_random_string(
        50,
        'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)',
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', '') and True or False
DBDEBUG = 'DB' in os.environ.get('DEBUG', '').split(',')
DEBUG_TEMPLATE = 'TEMPLATE' in os.environ.get('DEBUG', '').split(',')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '*').split(',')]


# Application definition

INSTALLED_APPS = [
    'leprikon.site',
    'leprikon',
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'cms',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'easy_thumbnails',
    'djangocms_column',
    'djangocms_link',
    'cmsplugin_filer_file',
    'cmsplugin_filer_folder',
    'cmsplugin_filer_image',
    'cmsplugin_filer_link',
    'cmsplugin_filer_teaser',
    'cmsplugin_filer_utils',
    'cmsplugin_filer_video',
    # leprikon dependecies
    'ganalytics',
    'raven.contrib.django.raven_compat',
    'social_django',
    'verified_email_field',
]

MIDDLEWARE_CLASSES = [
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'leprikon.middleware.LeprikonMiddleware',
]

ROOT_URLCONF = os.environ.get('ROOT_URLCONF', 'leprikon.site.urls')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ]
        },
    },
]

if DEBUG_TEMPLATE:
    TEMPLATES[0]['OPTIONS']['debug'] = True
    del TEMPLATES[0]['OPTIONS']['loaders']
    TEMPLATES[0]['APP_DIRS'] = True

WSGI_APPLICATION = os.environ.get('UWSGI_MODULE', 'leprikon.site.wsgi:application').replace(':', '.')

AUTHENTICATION_BACKENDS = [
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GooglePlusAuth',
    'verified_email_field.auth.VerifiedEmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', os.path.join(DATA_DIR, 'db.sqlite3')),
        'HOST': os.environ.get('DATABASE_HOST', None),
        'PORT': os.environ.get('DATABASE_PORT', None),
        'USER': os.environ.get('DATABASE_USER', None),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', None),
    }
}

if DATABASES['default']['ENGINE'].endswith('mysql'):
    DATABASES['default']['OPTIONS'] = {
        'init_command': (
            'ALTER DATABASE `{name}` DEFAULT CHARACTER SET utf8 COLLATE {collate}; '
            'SET default_storage_engine=INNODB; SET sql_mode=STRICT_TRANS_TABLES; '
            .format(
                name=DATABASES['default']['NAME'],
                collate=os.environ.get('DATABASE_COLLATE', 'utf8_bin'),
            )
        )
    }

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
] if not DEBUG else []


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGES = (
    ('cs', _('Czech')),
)

LANGUAGE_CODE = LANGUAGES[0][0]

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# set max upload size to 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'htdocs', 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'htdocs', 'static')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] if os.path.exists(os.path.join(BASE_DIR, 'static')) else []
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'staticfiles_downloader.DownloaderFinder',
]

# Logging
# https://docs.djangoproject.com/en/1.10/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': [],
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'handlers': ['console'],
        },
        'django.db.backends': {
            'level': 'DEBUG' if DBDEBUG else 'ERROR',
            'propagate': True,
        },
    },
}

try:
    import raven
except ImportError:
    pass
else:
    del raven
    if not DEBUG and os.environ.get('SENTRY_DSN'):
        # https://docs.sentry.io/clients/python/integrations/django/
        RAVEN_CONFIG = {
            'dsn': os.environ.get('SENTRY_DSN'),
        }

        LOGGING['filters'] = {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
        }
        LOGGING['handlers']['sentry'] = {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            # supports SENTRY_TAGS env var in form "tag1:value1,tag2:value2"
            'tags': dict(t.split(':', 1) for t in os.environ.get('SENTRY_TAGS', '').split(',') if ':' in t),
        }
        LOGGING['loggers']['raven'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
        LOGGING['loggers']['']['handlers'].append('sentry')

# Caching and session configuration
CACHES = {
    'default': {
        'BACKEND':    'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION':   os.environ.get('MEMCACHED_LOCATION', '127.0.0.1:11211'),
        'KEY_PREFIX': os.environ.get('MEMCACHED_KEY_PREFIX', 'leprikon'),
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Login / logout urls
LOGIN_URL = 'leprikon:user_login'
LOGOUT_URL = 'leprikon:user_logout'
LOGIN_REDIRECT_URL = 'leprikon:summary'

# Email configuration
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'leprikon@localhost')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_SUBJECT_PREFIX = os.environ.get('EMAIL_SUBJECT_PREFIX', '[Leprikón] ').strip() + ' '

# CMS configuration
# http://djangocms.readthedocs.io/en/latest/reference/configuration/
SITE_ID = 1

CMS_LANGUAGES = {
    SITE_ID: [{'code': l[0], 'name': l[1]} for l in LANGUAGES],
    'default': {
        'public': True,
        'fallbacks': [LANGUAGE_CODE],
        'hide_untranslated': True,
        'redirect_on_fallback': True,
    },
}

CMS_TEMPLATES = [
    ('leprikon/cms.html', 'Leprikon'),
]

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

THUMBNAIL_DEBUG = os.environ.get('DEBUG', False) == 'THUMBNAIL'

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

# Rocket.Chat URL
ROCKETCHAT_URL = os.environ.get('ROCKETCHAT_URL')

# Google Analytics configuration
GANALYTICS_TRACKING_CODE = os.environ.get('GANALYTICS_TRACKING_CODE')

# Social configuration
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')

SOCIAL_AUTH_GOOGLE_PLUS_SCOPE = ['profile', 'email']
SOCIAL_AUTH_GOOGLE_PLUS_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_PLUS_KEY')
SOCIAL_AUTH_GOOGLE_PLUS_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_PLUS_SECRET')

# Leprikon configuration
PRICE_DECIMAL_PLACES = 0
COUNTRIES_FIRST = ['CZ', 'SK']
