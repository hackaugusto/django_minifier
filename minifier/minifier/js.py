from itertools import groupby

from base import BaseMinifier
from minifier.minifier.tool.jsmin import jsmin

class Slimit(object):
    def minify(self, content):
        try:
            minify = self._minify
        except AttributeError:
            from slimit import minify
            self._minify = minify
            minify = self._minify

        return minify(content)

class JsMinifier(MinifierBase):
    def __init__(sefl):
        self._minify = Slimit()

    def minify(self, elements, name=None):
        output = ''

        # the scripts tags are grouped with previous sibiling if all the following is met:
        #   - both tags are both inline or in a file
        #       Because if the file is inline it is not intended for reuse, and minifying it together
        #       with the files that _are_ intended for reuse will lead to multiple download of this files
        #
        #   - if the use of the attributes 'async' or 'defer' match
        #       Because we need to preserve these attributes ... so they cannot be different
        for origin, el in [ {k,e} for k,e in self.js_group(elements)]:
            result = self._call_minify(el)

            #tag = '<script ' + ' '.join([ ''+ for k,v in el.attributes().iteritems() ])
            tag = '<script '

            # <script defer="defer" async
            for k,v in el.attributes.iteritems():
                if v=='' or v is None:
                    tag += '%s ' % k
                else:
                    tag += '%s="%s" ' % k,v

            if origin == 'file':
                if callable(name):
                    name = name(el)

                tag += 'src="%s"></script>' % self.save(result, name)
            else:
                tag += '>' + result + '</script>'

            output += tag

        return output

