from cee_config import read_local_settings, Config
import os

cfg = Config(os.path.join(os.path.dirname(__file__), ".."))

VAR_ROOT = cfg.dir("VAR_ROOT", default=os.path.join(cfg.project_root, "var"))
ALLOWED_HOSTS = cfg.list("ALLOWED_HOSTS", default=[])
CACHES = {
    "default": cfg.cache_url(default="locmem://")
}
DATABASES = {
    "default": cfg.db_url(default="mysql://root:root@localhost/some_random_project")
}
DEBUG = cfg.bool("DEBUG", default=False)
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = "django_cee_proto.urls"
SECRET_KEY = cfg.str("SECRET_KEY", default=("debug" if DEBUG else Config.NOT_SET))

MEDIA_ROOT = os.path.join(VAR_ROOT, "media")
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(VAR_ROOT, "static")
STATIC_URL = "/static/"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
WSGI_APPLICATION = "some_random_project.wsgi.application"

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

# TODO: Add project-specific settings here.

read_local_settings(globals())
