import types
import re

from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.utils.encoding import smart_unicode

class MinifierBase(object):
    def minify(self, elements):
        raise NotImplementedError

    def _call_minify(self, elements):
        content = ''

        for e in elements:
            content += e.get_content()
        return self._minify(content)

    def save(self, content, name=None):
        if name is None:
            raise ValueError('Name was not given.')

        storage = get_storage_class()

        # this should never happend
        if storage.exists(name):
            raise RuntimeError('Name conflict, ' + name + ' already exists.')

        storage.save(name, ContentFile(smary_unicode(content)))
        return storage.url(name)

    def js_properties(self, element):
        '''
        Return a string with the relevant attributes in the tag.

        The string is used to join the content of 'compatible' scripts,
        by compatible is meant that scripts with defer and/or async
        cannont be mixed with script that do not have defer or async.
        '''
        return { k:v for k,v in element.attributes().iteritems() if k in ['defer','async','src']}

    def js_group(self, elements, key=None):
        '''
        Return a iterator with the script tags that can be minified together.
        '''
        if key is None:
            # self.js_properties(x):
            #   js_properties filters the relevant properties from the tag
            #
            # .keys():
            #   for scripts only the propertie's name is relevant
            #
            # sorted():
            #   the order must be equal otherwise the grouping wont work
            #
            key = lambda x: ''.join(sorted(self.js_properties(x).keys()))

        return groupby(elements, key=key)

    def css_properties(self, element):
        '''
        Return a string with the relevant attributes in the tag.

        The string is used to join the content of 'compatible' css files,
        by compatible is meant that css files with different media queries
        cannont be joined
        '''
        return { k:v for k,v in element.attributes().iteritems() if k in ['media','scoped','href']}

    def css_group(self, elements, key=None):
        '''
        Return a iterator with the script tags that can be minified together.
        '''
        if key is None:
            def key(x):
                output = [] # using list because we sort the attributes

                # css_properties filters the relevant properties from the tag
                attrs = self.css_properties(x)

                # cant group different media queries
                for k,v in attrs.iteritems():
                    if k == 'media':
                        output.append(re.sub('\s','',k+v))
                    else:
                        output.append(k)

                # the order must be equal otherwise the grouping wont work
                return ''.join(sorted(output))

        return groupby(elements, key=key)


