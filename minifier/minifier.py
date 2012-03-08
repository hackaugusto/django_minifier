import os
import urllib
import md5

from django.utils.encoding import smart_unicode

from minifier.conf import settings
from minifier.utils import get_class
from minifier.utils.decorators import cached_property

class Minifier(object):

    def get_mimetype_minifier(self, mimetype):
        cls = [ cls for mime, cls in settings.minifiers if mime == mimetype ]

        if len(cls) == 0:
            raise ImproperlyConfigured('Missing minifier for %s mimetype.' % mimetype)

        return get_class(cls[0])

    def handle_mimetype(self, mimetype, elements, name=None):
        minifier = self.get_mimetype_minifier(mimetype)
        return smart_unicode(minifier.minify(elements, name))

    def get_parser(self):
        return get_class(settings.MINIFIER_PARSER)

    def minify(self, content, name):
        parser = self.get_parser()

        mime_group = {}
        minified = ''

        elements = parser.parse(content)

        # get all elements of the same mimetype ordered as seen
        for mimetype, element in parser.get_mimetypes(elements):
            try:
                listing = mime_group[mimetype]
            except KeyError e:
                listing = []
                mime_group[mimetype] = listing

            listing.append(element)

        # minify the elements
        for mimetype in mime_group.iterkeys():
            minified += self.handle_mimetype(mimetype, mime_group[mimetype], name);

        #minified = minified.encode(self.charset)
        return minified

def name_mangling(elements):
    data = ''

    for e in elements:
        data += e.filename()
        data += e.modified()

    return md5(data).hexdigest()

