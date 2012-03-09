from __future__ import absolute_import
import os.path
import urllib
import re

from django.core.files.storage import get_storage_class
try:
    from staticfiles import finders
except ImportError:
    from django.contrib.staticfiles import finders

from minifier.conf import settings

class ParserBase(object):
    """
    Base parser to be subclassed when creating an own parser.
    """
    def parse(self, content):
        """
        Return an iterable containing the elements inside content
        """
        raise NotImplementedError

class ElementProxy(object):
    def __init__(self, wrap, parser=None):
        self._wrap = wrap
        self._parser = parser

    def attributes(sefl):
        '''
        Must return a dictionary with the attributes and values set on the tag.
        '''
        raise NotImplementedError

    def whereis(self):
        '''
        Must return 'file' or 'inline'
        '''
        raise NotImplementedError

    def filename(self):
        raise NotImplementedError

    def modified(self):
        return str(os.path.getmtime(self.filename()))

    def filecontent(self):
        '''
        If the file is on a file should return its content
        '''
        raise NotImplementedError

    def inlinecontent(self):
        '''
        Must return the content inside the tag
        '''
        raise NotImplementedError

    def content(self):
        '''
        Returns the content of the file.

        This function calls self.inlinecontent() or self.filecontent()
        depending on self.whereis()
        '''
        if self.whereis() == 'inline':
            return self.inlinecontent()

        if self.whereis() == 'file':
            return self.filecontent()

        return ''

    def findfile(self, url):
        url = urllib.unquote(url).split("?", 1)[0]
        url = os.path.normpath(url.lstrip('/'))

        prefix = [ settings.STATIC_URL, settings.MEDIA_URL ]

        if settings.STATIC_URL[0] == '/':
            prefix.append(settings.STATIC_URL[1:])

        if settings.MEDIA_URL[0] == '/':
            prefix.append(settings.MEDIA_URL[1:])

        path = None
        for p in prefix:
            if p in url:
                length = url.find(p) + len(p)
                path = url[length:]

        if path:
            path = url
        else:
            raise Exception('Could not open the file %s' % url)

        return finders.find(path)

class ConditionalElementProxy(ElementProxy):
    conditional_regex = re.compile('<!--\[if\s+(?P<test>.*?)\s*\]>(?P<content>.*?)<!\[endif\]-->',re.DOTALL)

    def whereis(self):
        return 'inline'

    def get_test(self):
        return self.conditional_regex.match(self.content()).group('test')

    def get_inlinecontent(self):
        return self.conditional_regex.match(self.content()).group('content')

