import logging
import os

import dj_database_url


MAX_CONN_AGE = 600

logger = logging.getLogger(__name__)


def settings(config, *, databases=True, staticfiles=True, allowed_hosts=True, logging=True, secret_key=True):

    # Database configuration.
    # TODO: support other database (e.g. TEAL, AMBER, etc, automatically.)
    if databases:
        # Integrity check.
        if 'DATABASES' not in config:
            config['DATABASES'] = {'default': None}

        conn_max_age = config.get('CONN_MAX_AGE', MAX_CONN_AGE)
            
        if 'DATABASE_URL' in os.environ:
            logger.info('Adding $DATABASE_URL to default DATABASE Django setting.')

            # Configure Django for DATABASE_URL environment variable.
            config['DATABASES']['default'] = dj_database_url.config(conn_max_age=conn_max_age, ssl_require=True)

            logger.info('Adding $DATABASE_URL to TEST default DATABASE Django setting.')

            # Enable test database if found in CI environment.
            if 'CI' in os.environ:
                config['DATABASES']['default']['TEST'] = config['DATABASES']['default']

        else:
            logger.info('$DATABASE_URL not found, falling back to previous settings!')

    # Staticfiles configuration.
    if staticfiles:
        logger.info('Applying Staticfiles configuration to Django settings.')

        config['STATIC_ROOT'] = os.path.join(config['BASE_DIR'], 'staticfiles')
        config['STATIC_URL'] = '/static/'

        # Ensure STATIC_ROOT exists.
        os.makedirs(config['STATIC_ROOT'], exist_ok=True)

        # Insert Whitenoise Middleware.
        try:
            config['MIDDLEWARE_CLASSES'] = tuple(['whitenoise.middleware.WhiteNoiseMiddleware'] + list(config['MIDDLEWARE_CLASSES']))
        except KeyError:
            config['MIDDLEWARE'] = tuple(['whitenoise.middleware.WhiteNoiseMiddleware'] + list(config['MIDDLEWARE']))

        # Enable GZip.
        config['STATICFILES_STORAGE'] = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    if allowed_hosts:
        logger.info('Applying  ALLOWED_HOSTS configuration to Django settings.')
        config['ALLOWED_HOSTS'] = ['*']

    if logging:
        logger.info('Applying  logging configuration to Django settings.')

        config['LOGGING'] = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                               'pathname=%(pathname)s lineno=%(lineno)s ' +
                               'funcname=%(funcName)s %(message)s'),
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'simple': {
                    'format': '%(levelname)s %(message)s'
                }
            },
            'handlers': {
                'null': {
                    'level': 'DEBUG',
                    'class': 'logging.NullHandler',
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose'
                }
            },
            'loggers': {
                'testlogger': {
                    'handlers': ['console'],
                    'level': 'INFO',
                }
            }
        }

    # SECRET_KEY configuration.
    if secret_key:
        if 'SECRET_KEY' in os.environ:
            logger.info('Adding $SECRET_KEY to SECRET_KEY Django setting.')
            # Set the Django setting from the environment variable.
            config['SECRET_KEY'] = os.environ['SECRET_KEY']

