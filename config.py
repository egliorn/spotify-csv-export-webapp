from os import getenv


class Development:
    DEBUG = True
    SECRET_KEY = 'secret_key'

    LANGUAGES = ['en', 'ru']

    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300


class Deployment:
    SECRET_KEY = getenv('SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    LANGUAGES = ['en', 'ru']  # babel

    CACHE_TYPE = 'SimpleCache'  # flask-caching
    CACHE_DEFAULT_TIMEOUT = 300
