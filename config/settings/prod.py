from .base import *
from decouple import config
import dj_database_url

DEBUG = True
SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])

DATABASES = {
    "default": dj_database_url.config(
        default=f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}",
        conn_max_age=600
    )
}

MIDDLEWARE = ['django.middleware.security.SecurityMiddleware',
              'whitenoise.middleware.WhiteNoiseMiddleware'] + MIDDLEWARE

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.dropbox.DropBoxStorage",
        "OPTIONS": {
            "oauth2_access_token": os.getenv("DROPBOX_OAUTH2_ACCESS_TOKEN"),
            "oauth2_refresh_token": os.getenv("DROPBOX_OAUTH2_REFRESH_TOKEN"),
            "app_secret": os.getenv("DROPBOX_APP_SECRET"),
            "app_key": os.getenv("DROPBOX_APP_KEY"),
            "root_path": os.getenv("DROPBOX_ROOT_PATH", "/papers"),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
