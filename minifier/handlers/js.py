from __future__ import absolute_import

from itertools import groupby

from minifier.handlers.base import MinifierBase

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
    def __init__(self):
        self._minify = Slimit().minify

    def minify(self, elements, name):
        output = ''

        # the scripts tags are grouped with previous sibiling if all the following is met:
        #   - both tags are both inline or in a file
        #       Because if the file is inline it is not intended for reuse, and minifying it together
        #       with the files that _are_ intended for reuse will lead to multiple download of this files
        #
        #   - if the use of the attributes 'async' or 'defer' match
        #       Because we need to preserve these attributes ... so they cannot be different
        for group in [ list(v) for k,v in self.js_group(elements)]:

            name = self.resolve_name(elements, name) + '.js'
            if not self.compressed(name):
                result = self._call_minify(group)

            result = self._call_minify(group)
            one = group[0]

            #tag = '<script ' + ' '.join([ ''+ for k,v in el.attributes().iteritems() ])
            tag = '<script '

            # <script defer="defer" async
            properties = self.js_properties(one)
            if properties['src'] is not None:
                del properties['src']

            for k,v in properties.iteritems():
                if v=='' or v is None:
                    tag += '%s ' % k
                else:
                    tag += '%s="%s" ' % (k,v)

            if one.whereis() == 'file':
                url = self.compressed(name)
                if url is None:
                    tag += 'src="%s"></script>' % self.save(result, name)
                else:
                    tag += 'src="%s"></script>' % url
            else:
                tag += '>' + result + '</script>'

            output += tag

        return output
