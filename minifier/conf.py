import os
from django.conf import settings

from appconf import AppConf

class CompressorConf(AppConf):
    DISABLED = settings.DEBUG
    PARSER = 'minifier.parser.lxml.LxmlParser'
    MINIFIER_MINIFIERS = (
        ('application/javascript', 'minifier.handlers.js.JsMinifier'),
        ('text/css', 'minifier.handlers.css.CssMinifier'),
        ('text/plain','minifier.handlers.plain.PlainMinifier'),
        ('application/x-conditional-comment','minifier.handlers.comment.ConditionalCommentMinifier'),
    )

    CLOSURE_COMPILER_BINARY = 'java -jar compiler.jar'
    CSSTIDY_BINARY = 'csstidy'
    CSSTIDY_ARGUMENTS = '--template=highest'
    YUI_BINARY = 'java -jar yuicompressor.jar'
    YUI_CSS_ARGUMENTS = ''
    YUI_JS_ARGUMENTS = ''
    DATA_URI_MAX_SIZE = 1024

    class Meta:
        prefix = 'minifier'
