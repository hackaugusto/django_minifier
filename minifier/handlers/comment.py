from __future__ import absolute_import

from minifier.handlers.base import MinifierBase
from minifier.minifier import Minifier

class ConditionalCommentMinifier(MinifierBase):
    def minify(self, elements, name):
        output = ''
        minifier = Minifier()

        for e in elements:
            conditional = e.get_inlinecontent()

            output += minifier.minify(conditional,'minifier.minifier.name_mangling')
        return output


