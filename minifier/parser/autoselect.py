from django.utils.functional import LazyObject
from django.utils.importlib import import_module

class AutoSelectParser(LazyObject):
    options = ('minifier.parser.lxml.LxmlParser', 'minifier.parser.htmlparser')

    def __init__(self):
        self._wrapped = None

        for parser in self.options:
            try:
                module, attr = parser.rsplit('.',1)
                mod = import_module(module)
                parser = getattr(mod, attr)
                self._wrapped = parser()
                break
            except ImportError:
                continue

        raise ImportError('Missing parser')

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

