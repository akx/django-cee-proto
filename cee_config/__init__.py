# -*- coding: utf-8 -*-
import json

import dj_database_url
import django_cache_url
import os


try:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

try:
    text_type = unicode
except NameError:
    text_type = str

__all__ = ("Environ", "read_local_settings")


def split(value):
    return text_type(value).split(",")


class Environ(object):
    NOT_SET = object()

    def __init__(self, project_root, filename=None, section=None):
        self._env = os.environ.copy()
        self.project_root = os.path.realpath(project_root)
        if not os.path.isdir(self.project_root):
            raise ValueError("Invalid project_root: %r" % project_root)
        if filename:
            self.read(filename, section)

    def _get_value(self, var, cast, default=NOT_SET):
        if var not in self._env:
            if default is Environ.NOT_SET:
                raise ValueError("The %s variable is required" % var)
            return default
        return cast(self._env[var])

    def read(self, filename, section=None):
        if not os.path.isfile(filename):
            return
        p = ConfigParser()
        p.read([filename])
        for section in ([section] if section else p.sections()):
            self._env.update(p.items(section))

    def str(self, var, default=NOT_SET):
        return self._get_value(var, cast=text_type, default=default)

    def bool(self, var, default=NOT_SET):
        return self._get_value(var, cast=bool, default=default)

    def int(self, var, default=NOT_SET):
        return self._get_value(var, cast=int, default=default)

    def float(self, var, default=NOT_SET):
        return self._get_value(var, cast=float, default=default)

    def json(self, var, default=NOT_SET):
        return self._get_value(var, cast=json.loads, default=default)

    def list(self, var, cast=None, default=NOT_SET):
        return self._get_value(var, cast=split, default=default)

    def db_url(self, var="DATABASE_URL", default=NOT_SET, **kwargs):
        url = self._get_value(var, cast=text_type, default=default)
        return dict(dj_database_url.parse(url), **kwargs)

    def cache_url(self, var="CACHE_URL", default=NOT_SET, **kwargs):
        url = self._get_value(var, cast=text_type, default=default)
        return dict(django_cache_url.parse(url), **kwargs)

    def dir(self, var, default=NOT_SET):
        path = self._get_value(var, cast=text_type, default=default)
        path = os.path.realpath(path)
        if not os.path.isdir(path):
            raise ValueError(
                "The directory %r (%r) does not exist" % (path, var)
            )
        return path


def vars_in_namespace(namespace):
    if not hasattr(namespace, "items"):
        namespace = vars(namespace)
    return dict((k, v) for k, v in namespace if k.isupper())


def read_local_settings(namespace):
    try:
        import local_settings
    except ImportError:
        local_settings = None

    if local_settings:
        namespace.update(vars_in_namespace(local_settings))
        if hasattr(local_settings, "configure"):
            settings = vars_in_namespace(namespace)
            namespace.update(local_settings.configure(settings) or {})
