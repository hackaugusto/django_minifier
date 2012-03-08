from django import template
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from minifier.conf import settings
from minifier.minifier import Minifier

register = template.Library()

class MinifierNode(template.Node):

    def __init__(self, nodelist, name=None):
        '''
        This node parsers the html and compress what it can
        '''
        self.nodelist = nodelist or template.NodeList() # probably dont need this
        if name is not None:
            name = import_module(name)

        self.name = name

        # tries to compile now if there is no other tags
        # because there is no other tags we can safely give it a {} as context
        if not self.nodelist.contains_nontext:
            minifier = Minifier()

            try:
                compressed_data = minifier.minify(nodelist.render({}), {}, self.name)
                if cache_key:
                    cache_set(cache_key, compressed_data)
            except Exception, e:
                # don't do anything in production
                if settings.DEBUG:
                    raise e

    def render(self, context):
        rendered = self.nodelist.render(context)

        if settings.DEBUG or setting.MINIFY_DISABLED:
            return rendered

        minifier = Minifier()

        try:
            return minifier.minify(rendered, self.name)
        except Exception, e:
            # don't do anything in production
            if settings.DEBUG:
                raise e

@register.tag
def minify(parser, token):
    """
    Minify the css and javascript between the tag.

    The tag groups css files before js, respecting the order that they appear in the document.
    The tag does not remove conditional comments used by IE

    Example:

        {% minify %}
        <script src="/media/js/one.js" type="text/javascript" charset="utf-8"></script>
        <script type="text/javascript" charset="utf-8">obj.value = "value";</script>
        <!--[if IE]>
        <script type="text/javascript" charset="utf-8">obj.value = "othervalue";</script>
        <![endif]-->
        <link rel="stylesheet" href="/media/css/one.css" type="text/css" charset="utf-8">
        <link rel="stylesheet" href="/media/css/two.css" type="text/css" charset="utf-8">
        <style type="text/css">p { border:5px solid green;}</style>
        {% minify %}

    Which would be rendered something like:

        <link rel="stylesheet" href="/media/CACHE/css/f7c661b7a124.css" type="text/css" media="all" charset="utf-8">
        <style type="text/css">p { border:5px solid green;}</style>
        <script type="text/javascript" src="/media/CACHE/js/3f33b9146e12.js" charset="utf-8"></script>
        <!--[if IE]>
        <script type="text/javascript" charset="utf-8">obj.value = "othervalue";</script>
        <![endif]-->
    """

    args = token.split_contents()

    if len(args) > 2:
        raise template.TemplateSyntaxError(
            "Too many arguments for %r." % args[0])

    nodelist = parser.parse(('endcompress',))
    parser.delete_first_token()

    if len(args) == 2:
        name = args[1]
    else:
        name = 'minifier.minifier.name_mangling'
    return MinifierNode(nodelist, name=name)
