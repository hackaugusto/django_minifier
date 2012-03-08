from __future__ import absolute_import
import os
import urllib
from md5 import md5

from django.utils.encoding import smart_unicode
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from minifier.conf import settings
from minifier.utils.decorators import cached_property

class Minifier(object):

    def get_mimetype_minifier(self, mimetype):
        cls = [ cls for mime, cls in settings.MINIFIER_MINIFIERS if mime == mimetype ]

        if len(cls) == 0:
            raise ImproperlyConfigured('Missing minifier for %s mimetype.' % mimetype)

        module, attr = cls[0].rsplit('.',1)
        mod = import_module(module)
        return getattr(mod, attr)()

    def handle_mimetype(self, mimetype, elements, name=None):
        minifier = self.get_mimetype_minifier(mimetype)
        return minifier.minify(elements, name)

    def get_parser(self):
        module, attr = settings.MINIFIER_PARSER.rsplit('.',1)
        mod = import_module(module)
        return getattr(mod, attr)()

    def minify(self, content, name):
        parser = self.get_parser()

        mime_group = {}
        minified = ''

        elements = parser.parse(content)

        # get all elements of the same mimetype ordered as seen
        for mimetype, element in parser.get_mimetypes(elements):
            try:
                listing = mime_group[mimetype]
            except KeyError, e:
                listing = []
                mime_group[mimetype] = listing

            listing.append(element)

        # minify the elements
        for mimetype in mime_group.iterkeys():
            minified += self.handle_mimetype(mimetype, mime_group[mimetype], name);

        return minified

def name_mangling(string):
    return md5(string).hexdigest()

