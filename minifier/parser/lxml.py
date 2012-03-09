from __future__ import absolute_import, with_statement
import codecs
import lxml
from lxml import etree
from lxml.etree import tostring
from lxml.html import fromstring, soupparser

from django.core.exceptions import ImproperlyConfigured

from minifier.parser.base import ConditionalElementProxy, ElementProxy, ParserBase

conditional_regex = ConditionalElementProxy.conditional_regex

class CssElement(ElementProxy):
    def attributes(self):
        return dict(self._wrap.attrib)

    def whereis(self):
        if self._wrap.tag == 'link':
            return 'file'

        elif self._wrap.tag == 'style':
            return 'inline'

    def filename(self):
        if self._wrap.tag == 'link':
            return self.findfile(self._wrap.get('href'))

    def filecontent(self):
        if self._wrap.tag == 'link':
            filename = self.findfile(self._wrap.get('href'))

            with codecs.open(filename, 'rb', 'utf_8') as fd:
                return fd.read()

    def inlinecontent(self):
        return self._wrap.text

class JsElement(ElementProxy):
    def attributes(self):
        return dict(self._wrap.attrib)

    def whereis(self):
        if self._wrap.get('src') is None:
            return 'inline'

        return 'file'

    def filename(self):
        return self.findfile(self._wrap.get('src'))

    def filecontent(self):
        filename = self.findfile(self._wrap.get('src'))

        with codecs.open(filename, 'rb', 'utf_8') as fs:
            return fs.read()

    def inlinecontent(self):
        return self._wrap.text

class ConditionalCommentElement(ConditionalElementProxy):
    def attributes(self):
        match = conditional_regex.search(self._wrap.text)

        attrs = {}
        if match:
            attrs['condition'] = match.group()

        return attrs

    def inlinecontent(self):
        return '<!--' + self._wrap.text + '-->'

class PlainElement(ElementProxy):
    def attributes(self):
        return {}

    def whereis(self):
        return 'inline'

    def inlinecontent(self):
        return etree.tostring(self._wrap)

class LxmlParser(ParserBase):

    def parse(self, content):
        tree = fromstring('<root>%s</root>' % content)

        try:
            ignore = tostring(tree, encoding=unicode)
        except UnicodeDecodeError:
            tree = soupparser.fromstring(content)

        return tree

    def get_mimetypes(self, elements):
        ordered = []

        for elem in elements:
            tag = elem.tag

            if elem.tag is etree.Comment:
                # str(elem) returns the comment start '<!--' and comment end '-->'
                # elem.text returns without
                print(str(elem))
                if conditional_regex.match(str(elem)):
                    print('conditional')
                    ordered.append( ('application/x-conditional-comment', ConditionalCommentElement(elem)) )

                # ignore another comments

            elif tag == 'style' or (tag == 'link' and elem.get('rel') == 'stylesheet'):
                ordered.append( ('text/css', CssElement(elem)) )

            elif tag == 'script' and (elem.get('language') == None or elem.get('language') == '' or elem.get('language') == 'javascript'):
                ordered.append( ('application/javascript', JsElement(elem)) )

            else:
                ordered.append( ('text/plain', PlainElement(elem)) )

        return ordered

    def get_mimetypes_grouped(self, elements):
        mime_group = {}

        # cant find the comments that have conditionals with xpath
        for comm in elements.iterchildren(tag=etree.Comment):
            for conditional in conditional_regex.findall(comm.text):
                l = mime_group.get('application/x-conditional-comment') or []
                l.append(conditional)
                mime_group['application/x-conditional-comment'] = l

        css = elements.xpath('/link[@rel="stylesheet"]|style')
        if len(css) != 0:
            mime_group['text/css'] = [ CssElement(e) for e in css ]

        js = elements.xpath('script[not(@language) or @language="" or @language="javascript"]')
        if len(js) != 0:
            mime_group['application/js'] = [ JsElement(e) for e in js ]

        return mime_group
