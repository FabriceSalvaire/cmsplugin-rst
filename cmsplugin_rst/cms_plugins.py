# -*- coding: utf-8 -*-

####################################################################################################

from django import template
from django.conf import settings
from django.utils.encoding import force_text, force_bytes
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import RstPluginForm
from .models import RstPluginModel, RstImage
from .utils import postprocess, get_cfg, french_insecable

try:
    from docutils.core import publish_parts

    # We register custom docutils directives, roles etc.
    from . import docutils_plugins
    from . import pygments_directive
    from . import cms_directive
except ImportError:
    publish_parts = None

####################################################################################################

DOCUTILS_RENDERER_SETTINGS = {
    'initial_header_level': 1,
    # important, to have even lone titles stay in the html fragment:
    'doctitle_xform': False,
    # we also disable the promotion of lone subsection title to a subtitle:
    'sectsubtitle_xform': False,
    'file_insertion_enabled': False,  # SECURITY MEASURE (file hacking)
    'raw_enabled': False, # SECURITY MEASURE (script tag)
    'report_level': 2, # report warnings and above, by default
}
DOCUTILS_RENDERER_SETTINGS.update(get_cfg('SETTINGS_OVERRIDES', {}))

####################################################################################################

# https://docutils.readthedocs.io/en/sphinx-docs/index.html

def restructured_text(value, header_level=None, report_level=None):

    if publish_parts is not None:
        settings_overrides = DOCUTILS_RENDERER_SETTINGS.copy()
        if header_level is not None: # starts from 1
            settings_overrides['initial_header_level'] = header_level
        if report_level is not None: # starts from 1 too
            settings_overrides['report_level'] = 0 # report_level
        parts = publish_parts(source=force_bytes(value),
                              writer_name=get_cfg('WRITER_NAME', 'html4css1'),
                              settings_overrides=settings_overrides)
        # http://docutils.sourceforge.net/docs/api/publisher.html
        return force_text(parts['html_body']) # parts['body_pre_docinfo'] + parts['fragment']
    else:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in 'restructuredtext' filter: "
                                               "The Python docutils library isn't installed.")
        return force_text(value)

####################################################################################################

def render_rich_text(rst_string, language_code='', header_level=None, report_level=None):

    rst = get_cfg('CONTENT_PREFIX', '') + '\n'
    rst += rst_string
    rst += '\n' + get_cfg('CONTENT_SUFFIX', '')
    rst = rst.replace('{{ MEDIA_URL }}', settings.MEDIA_URL)
    rst = rst.replace('{{ STATIC_URL }}', settings.STATIC_URL)

    content = restructured_text(rst, header_level=header_level, report_level=report_level)
    content = content.replace('{{ BR }}', '<br/>')
    content = content.replace('{{ NBSP }}', '&nbsp;')

    if language_code.lower().startswith('fr'): # ONLY french codes should start like that
        content = french_insecable(content)

    content = postprocess(content)

    return content

####################################################################################################

class RstImagePlugin(CMSPluginBase):

    model = RstImage
    name = _("RST Image")
    require_parent = True
    parent_classes = ['RstPlugin']
    render_plugin = False
    # render_template = "cmsplugin_svg/plugin.html"

    # Editor fieldsets
    fieldsets = (
        (None, {
            'fields': ('svg_image',
                       'tag_type',
                       'height', 'width',
                       'alignment',
                       'caption_text',
                       'alt_text')
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'additional_class_names',
                'label',
                'id_name',
            ),
        }),
    )

####################################################################################################

class RstPlugin(CMSPluginBase):

    name = _('Restructured Text Plugin')
    render_template = 'cms/content.html'
    model = RstPluginModel
    form = RstPluginForm
    allow_children = True
    child_classes = ['RstImagePlugin']

    ##############################################

    def render(self, context, instance, placeholder):

        if instance.child_plugin_instances is not None:
            for i in instance.child_plugin_instances:
                print("child", i, type(i))

        # We lookup cms page language, else i18n language
        language_code = context.get('lang', '') or context.get('LANGUAGE_CODE', '')
        content = render_rich_text(instance.body,
                                   language_code=language_code,
                                   header_level=instance.header_level,
                                   report_level=None) # not set ATM
        context.update({'content': mark_safe(content)})
        return context

####################################################################################################

plugin_pool.register_plugin(RstImagePlugin)
plugin_pool.register_plugin(RstPlugin)
