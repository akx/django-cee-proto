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

__all__ = ("Config", "read_local_settings")


def to_list(value):
    if isinstance(value, (text_type, str)):
        return list(text_type(value).split(","))
    return list(value)


NOT_SET = object()


class Config(object):
    NOT_SET = NOT_SET

    def __init__(self, project_root, env_file=None):
        self.project_root = os.path.realpath(project_root)
        if not os.path.isdir(self.project_root):
            raise ValueError("Invalid project_root: %r" % project_root)
        self._data = {}
        self._data.update(os.environ)
        package_json = os.path.join(self.project_root, "package.json")
        if os.path.isfile(package_json):
            with file(package_json) as fp:
                self._data.update(
                    ("PACKAGE_%s" % k.upper(), v)
                    for (k, v) in
                    json.load(fp).items()
                )

        if env_file and os.path.isfile(env_file):
            self.read_env(env_file)

    def read_env(self, filename, section=None):
        p = ConfigParser()
        p.read([filename])
        for section in ([section] if section else p.sections()):
            self._data.update(p.items(section))

    def _get_value(self, var, cast, default=NOT_SET):
        if var not in self._data:
            if default is NOT_SET:
                raise ValueError("The %s variable is required" % var)
            return default
        return cast(self._data[var])

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
        return self._get_value(var, cast=to_list, default=default)

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
