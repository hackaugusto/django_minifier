from __future__ import absolute_import

from minifier.handlers.base import MinifierBase

class PlainMinifier(MinifierBase):
    def minify(self, elements, name):
        output = ''
        for e in elements:
            output += e.content()
        return output

