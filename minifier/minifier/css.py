from itertools import groupby

from base import BaseMinifier
from minifier.minifier.tool

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
        self._minify = Cssmin()

    def minify(self, elements, name=None):
        output = ''

        # the scripts tags are grouped with previous sibiling if all the following is met:
        #   - both tags are both inline or in a file
        #       Because if the file is inline it is not intended for reuse, and minifying it together
        #       with the files that _are_ intended for reuse will lead to multiple download of this files
        #
        #   - if the use of the attributes 'async' or 'defer' match
        #       Because we need to preserve these attributes ... so they cannot be different
        for origin, el in [ {k,e} for k,e in self.css_group(elements)]:
            result = self._call_minify(el)

            if origin == 'file':
                tag = '<link '
            else:
                tag = '<style '

            # <tag media="print" scoped
            for k,v in el.attributes.iteritems():
                if v=='' or v is None:
                    tag += '%s ' % k
                else:
                    tag += '%s="%s" ' % k,v

            if origin == 'file':
                if callable(name):
                    name = name(el)

                tag += 'href="%s" />' % self.save(result, name)
            else:
                tag += '>' + result + '</style>'

            output += tag

        return output

