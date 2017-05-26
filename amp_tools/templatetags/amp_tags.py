# -*- coding: utf-8 -*-
from django.conf import settings

from compressor.css import CssCompressor
from compressor.templatetags.compress import CompressorMixin, OUTPUT_FILE, OUTPUT_MODES, OUTPUT_INLINE
from django import template
from django.core.files.base import ContentFile
from django.template.base import TextNode
from django.utils.safestring import mark_safe

register = template.Library()

AMP_CHARSET = '<meta charset="utf-8">'
AMP_BASE_SCRIPT = '<script async src="https://cdn.ampproject.org/v0.js"></script>'
AMP_HEAD_STYLE = '<style amp-boilerplate>body{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}@-webkit-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-moz-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-ms-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-o-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}</style><noscript><style amp-boilerplate>body{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}</style></noscript>'


@register.tag('amplify')
def amplify(parser, token):
    nodelist = parser.parse(('endamplify',))
    parser.delete_first_token()
    return AmpNode(nodelist)


class AmpNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        request = context.request
        if request.is_amp:
            self.set_canonical(request)
            self.amplify_setup()
            self.amplify_images()

        output = self.nodelist.render(context)
        return output

    def add_closing_tag(self, tag, node, next_close):
        pos = 0
        while True:
            if not next_close:
                pos = node.s.find('<'+tag, pos)
                if pos == -1:
                    break
            pos = node.s.find('>', pos)
            if pos == -1:
                return True
            node.s = node.s[0:pos + 1] + '</' + tag + '>' + node.s[pos + 1:]
            next_close = False
        return next_close

    def set_canonical(self, request):
        request.canonical = 'https://www.blueshoe.de'
        self.canonical_link = '<link rel="canonical" href="{}" />'.format(request.canonical)

    def amplify_images(self):
        next_close = False
        for node in self.nodelist:
            if isinstance(node, TextNode):
                node.s = node.s.replace('img', 'amp-img')
                next_close = self.add_closing_tag('amp-img', node, next_close)

    def add_html_amp_attribute(self):
        for node in self.nodelist:
            if isinstance(node, TextNode):
                node.s = node.s.replace('<html', '<html amp')

    # Set all the things amp wants us to set in the <head> section
    def setup_head(self):
        for node in self.nodelist:
            if isinstance(node, TextNode):
                pos = 0
                while True:
                    pos = node.s.find('<' + 'head', pos)
                    if pos == -1:
                        break
                    pos = node.s.find('>', pos)
                    node.s = node.s[0:pos + 1] + AMP_CHARSET + AMP_BASE_SCRIPT + AMP_HEAD_STYLE + \
                             settings.AMP_HEAD_VIEWPORT + self.canonical_link + node.s[pos + 1:]

    # We set the charset to utf-8 so we have to remove currently existing ones.
    def remove_charset(self):
        for node in self.nodelist:
            if isinstance(node, TextNode):
                # If there is not charset in this node anyway return
                charset_index = node.s.find('charset')
                if charset_index == -1:
                    continue
                pos = 0
                while True:
                    pos = node.s.find('<' + 'meta', pos)
                    if pos == -1:
                        break
                    pos_end = node.s.find('>', pos)
                    if charset_index > pos and charset_index < pos_end:
                        node.s = node.s[0:pos] + node.s[pos_end + 1:]

    def amplify_setup(self):
        self.add_html_amp_attribute()
        self.remove_charset()
        self.setup_head()

class AmpCompressorMixin(CompressorMixin):

    @property
    def compressors(self):
        return {
            'js': settings.COMPRESS_JS_COMPRESSOR,
            'css': settings.COMPRESS_CSS_COMPRESSOR,
            'amp_css': 'amp_tools.templatetags.amp_tags.AmpCssCompressor'
        }

class AmpCompressorNode(AmpCompressorMixin, template.Node):

    def __init__(self, nodelist, kind=None, mode=OUTPUT_FILE, name=None):
        self.nodelist = nodelist
        self.kind = kind
        self.mode = mode
        self.name = name

    def get_original_content(self, context):
        return self.nodelist.render(context)

    def render(self, context, forced=False):

        # Check if in debug mode
        if self.debug_mode(context):
            return self.get_original_content(context)

        css = self.render_compressed(context, self.kind, self.mode, forced=True)
        context.request.css = css
        return css


@register.tag
def amp_compress(parser, token):
    nodelist = parser.parse(('endamp_compress',))
    parser.delete_first_token()

    args = token.split_contents()

    if not len(args) in (2, 3, 4):
        raise template.TemplateSyntaxError(
            "%r tag requires either one, two or three arguments." % args[0])

    kind = args[1]

    if len(args) >= 3:
        mode = args[2]
        if mode not in OUTPUT_MODES:
            raise template.TemplateSyntaxError(
                "%r's second argument must be '%s' or '%s'." %
                (args[0], OUTPUT_FILE, OUTPUT_INLINE))
    else:
        mode = OUTPUT_FILE
    if len(args) == 4:
        name = args[3]
    else:
        name = None
    return AmpCompressorNode(nodelist, kind, mode, name)


class AmpCssCompressor(CssCompressor):

    def output_file(self, mode, content, forced=False, basename=None):
        """
        The output method that saves the content to a file and renders
        the appropriate template with the file's URL.
        """
        new_filepath = self.get_filepath(content, basename=basename)
        self.context.request.amp_css_path = new_filepath
        if not self.storage.exists(new_filepath) or forced:
            self.storage.save(new_filepath, ContentFile(content.encode(self.charset)))
        url = mark_safe(self.storage.url(new_filepath))
        return self.render_output(mode, {"url": url})

    def get_template_name(self, mode):
        if self.context.request.is_amp:
            return 'amp_css_inline.html'
        else:
            return super(AmpCssCompressor, self).get_template_name(mode)