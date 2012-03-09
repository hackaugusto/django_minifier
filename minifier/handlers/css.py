from __future__ import absolute_import

from itertools import groupby

from minifier.handlers.base import MinifierBase

class Cssmin(object):
    def minify(self, content):
        try:
            minify = self._minify
        except AttributeError:
            from cssmin import cssmin
            self._minify = cssmin
            minify = self._minify

        return minify(content)

class CssMinifier(MinifierBase):
    def __init__(self):
        self._minify = Cssmin().minify

    def minify(self, elements, name):
        output = ''

        # the scripts tags are grouped with previous sibiling if all the following is met:
        #   - both tags are both inline or in a file
        #       Because if the file is inline it is not intended for reuse, and minifying it together
        #       with the files that _are_ intended for reuse will lead to multiple download of this files
        #
        #   - if the use of the attributes 'async' or 'defer' match
        #       Because we need to preserve these attributes ... so they cannot be different
        for group in [ list(v) for k,v in self.css_group(elements)]:

            name = self.resolve_name(elements, name) + '.css'
            if not self.compressed(name):
                result = self._call_minify(group)

            one = group[0]

            if one.whereis() == 'file':
                tag = '<link '
            else:
                tag = '<style '

            # <tag media="print" scoped
            properties = self.css_properties(one)
            if properties['href'] is not None:
                del properties['href']

            for k,v in properties.iteritems():
                if v=='' or v is None:
                    tag += '%s ' % k
                else:
                    tag += '%s="%s" ' % (k,v)

            if one.whereis() == 'file':
                url = self.compressed(name)
                if not url:
                    tag += 'href="%s" />' % self.save(result, name)
                else:
                    tag += 'href="%s" />' % url
            else:
                tag += '>' + result + '</style>'

            output += tag

        return output

