from __future__ import absolute_import
import os
import urllib
from md5 import md5
import inspect

from django.utils.encoding import smart_unicode
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from minifier.conf import settings
from minifier.utils.decorators import cached_property

class Minifier(object):

    def get_mimetype_minifier(self, mimetype):
        cls = [ cls for mime, cls in settings.MINIFIER_MINIFIERS if mime == mimetype ][0]

        if len(cls) == 0:
            raise ImproperlyConfigured('Missing minifier for %s mimetype.' % mimetype)

        module, attr = cls.rsplit('.',1)
        mod = import_module(module)
        handler = getattr(mod, attr)

        if not inspect.isclass(handler):
            raise ImproperlyConfigured('Handler(%s) for "%s" is not a class object' % (cls, mimetype))

        return handler()

    def handle_mimetype(self, mimetype, elements, name=None):
        minifier = self.get_mimetype_minifier(mimetype)
        return minifier.minify(elements, name)

    def get_parser(self):
        module, attr = settings.MINIFIER_PARSER.rsplit('.',1)
        mod = import_module(module)
        parser = getattr(mod, attr)

        if not inspect.isclass(parser):
            raise ImproperlyConfigured('Parser(%s) is not a class object' % settings.MINIFIER_PARSER)

        return parser()

    def minify(self, content, name):
        parser = self.get_parser()
        elements = parser.parse(content)

        # get all elements of the same mimetype ordered as seen
        mime_group = {}
        mime_order = []
        for mimetype, element in parser.get_mimetypes(elements):
            try:
                mime_group[mimetype].append(element)
            except KeyError:
                l = []
                l.append(element)
                mime_group[mimetype] = l

            if mimetype not in mime_order:
                if mimetype == 'text/css' and 'application/javascript' in mime_order:
                    mime_order.insert(mime_order.index('application/javascript'),'text/css')

                # if js is after css, we are good, otherwise the rule above fix it
                else:
                    mime_order.append(mimetype)

        # minify the elements
        minified = ''
        for mimetype in mime_order:
            minified += self.handle_mimetype(mimetype, mime_group[mimetype], name);

        return minified

def name_mangling(string):
    return md5(string).hexdigest()

