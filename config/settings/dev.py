from .base import *
from decouple import config

DEBUG = config("DEBUG", default=True, cast=bool)
SECRET_KEY = config("SECRET_KEY", default="dev-secret")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost",
                        cast=lambda v: [s.strip() for s in v.split(",")])

INSTALLED_APPS += ["django_extensions"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

STORAGES = {
    "default": {
        "BACKEND": "base.storages.WindowsCompatibleDropboxStorage",
        "OPTIONS": {
            "oauth2_access_token": os.getenv("DROPBOX_OAUTH2_ACCESS_TOKEN"),
            "oauth2_refresh_token": os.getenv("DROPBOX_OAUTH2_REFRESH_TOKEN"),
            "app_secret": os.getenv("DROPBOX_APP_SECRET"),
            "app_key": os.getenv("DROPBOX_APP_KEY"),
            "root_path": os.getenv("DROPBOX_ROOT_PATH"),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
