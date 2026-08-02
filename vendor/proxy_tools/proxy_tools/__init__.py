"""Maintained local replacement for the pywebview ``proxy_tools`` dependency.

Pywebview needs a lazy proxy only for a handful of deprecated module-level
properties. The original package does not build on recent Python releases.
"""


class Proxy:
    __slots__ = ("__local", "__dict__", "__name__")

    def __init__(self, local, name=None):
        object.__setattr__(self, "_Proxy__local", local)
        object.__setattr__(self, "__name__", name)

    def _get_current_object(self):
        return self.__local()

    @property
    def __dict__(self):
        return self._get_current_object().__dict__

    def __getattr__(self, name):
        return getattr(self._get_current_object(), name)

    def __repr__(self):
        return repr(self._get_current_object())

    def __str__(self):
        return str(self._get_current_object())

    def __bool__(self):
        return bool(self._get_current_object())

    def __call__(self, *args, **kwargs):
        return self._get_current_object()(*args, **kwargs)

    def __iter__(self):
        return iter(self._get_current_object())

    def __getitem__(self, item):
        return self._get_current_object()[item]

    def __len__(self):
        return len(self._get_current_object())


module_property = Proxy
proxy = Proxy
