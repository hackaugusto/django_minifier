from os import path
import urllib

from django.contrib.staticfiles import finders
from django.config import settings

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
        return path.getmtime(self.filename())

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
        url = path.normpath(url.lstrip('/'))

        if settings.STATIC_URL in url:
            path = url[ url.find(settings.STATIC_URL) + len(settings.STATIC_URL) ]

        elif settings.MEDIA_URL in url:
            path = url[ url.find(settings.MEDIA_URL) + len(settings.MEDIA_URL) ]

        path = finders.find(path)

        return path

