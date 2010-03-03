# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms import widgets
from django.forms.util import flatatt
from django.template import Context, Template
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

GEOMETRY_TEMPLATE = u"""{% load i18n %}<span class="geometry">
<div style="display: none;">
    <div id="{{ geometry_field_id }}geom-info-window">
        <select id="{{ geometry_field_id }}geom-type">
            <option value="P" selected="selected">{% trans "Point" %}</option>
            <option value="C">{% trans "Circle" %}</option>
            <option value="L">{% trans "Polygon" %}</option>
            <option value="H">{% trans "Handwriting" %}</option>
        </select> <a href="" id="{{ geometry_field_id }}geom-reset" style="display: none;">{% trans "Reset" %}</a>
        <div id="{{ geometry_field_id }}geom-type-point">
            <div>{% trans "Place" %}: <span id="{{ geometry_field_id }}geom-point"></span></div>
            <div class="small">{% trans "Accuracy" %}: <span id="{{ geometry_field_id }}geom-accuracy"></span></div>
        </div>
        <div id="{{ geometry_field_id }}geom-type-circle">
            <div class="slider"></div>
            <div>{% trans "Radius" %}: <span id="{{ geometry_field_id }}geom-radius">0 m</span></div>
        </div>
        <div id="{{ geometry_field_id }}geom-type-polygon">
            <div>{% trans "Area" %}: <span id="{{ geometry_field_id }}geom-area">0 m²</span></div>
            <div>{% trans "Vertexes" %}: <span id="{{ geometry_field_id }}geom-vertexes">4</span></div>
            <div class="small">{% trans "Click node to add one. Right click to remove." %}</div>
        </div>
    </div>
    {% if geometry_update_address_field %}
    <input type="hidden" id="{{ geometry_field_id }}geom-update-address"
           value="{{ geometry_update_address_field }}">
    {% endif %}
</div>
<span class="_polygon-field-js" style="display: none;">{{ geometry_field_id }}</span>
<div id="{{ geometry_field_id }}geom-map" style="display: none;" {{ geometry_attrs }}></div>
</span>"""


class GeometryTextarea(forms.Textarea):

    class Media:
        css = {'all': ['%scss/geometry.css' % settings.MEDIA_URL]}
        js = ['http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
              'http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/jquery-ui.min.js',
              '%sjs/geometry.js' % settings.MEDIA_URL]

    def __init__(self, attrs=None, update_address_field=None):
        super(GeometryTextarea, self).__init__(attrs)
        self.update_address_field = update_address_field

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        value = force_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)
        textarea_output = mark_safe(u'<textarea%s>%s</textarea>'
                                    % (flatatt(final_attrs),
                                       conditional_escape(force_unicode(value))))
        geometry_context = Context({'geometry_field_id': final_attrs.get('id'),
                                    'geometry_attrs': mark_safe(flatatt(self.attrs)),
                                    'geometry_update_address_field': self.update_address_field})
        geometry_template = Template(GEOMETRY_TEMPLATE)
        geometry_output = mark_safe(geometry_template.render(geometry_context))
        return mark_safe(u"%s%s" % (textarea_output, geometry_output))


class AnchorWidget(widgets.Widget):

    def __init__(self, text_shown=None, attrs=None, *args, **kwargs):
        super(AnchorWidget, self).__init__(*args, **kwargs)
        self.attrs = attrs or {}
        self.text_show = text_shown or _('Click here')

    def render(self, name, value=None, attrs=None):
        self.attrs.update(attrs or {})
        final_attrs = self.build_attrs(self.attrs, name=name)
        return mark_safe(u'<a%s >%s</a>' % (flatatt(final_attrs),
                                            value or self.text_show))


class GoogleImagesSearchInput(widgets.TextInput):

    class Media:
        js = ['http://www.google.com/jsapi',
              '%sjs/googleimagessearchinput.js' % settings.MEDIA_URL]


class OlWidgetGoogleMapsSearch(widgets.TextInput):

    class Media:
        js = ['http://www.google.com/jsapi',
              '%sjs/olwidgetgooglemapssearch.js' % settings.MEDIA_URL]

    def __init__(self, *args, **kwargs):
        self.olwidget_maps = kwargs.pop('olwidget_maps', None)
        super(OlWidgetGoogleMapsSearch, self).__init__(*args, **kwargs)

    def render(self, name, value=None, attrs=None):
        if self.olwidget_maps:
            attrs.update({'olwidget_maps': self.olwidget_maps})
        return super(OlWidgetGoogleMapsSearch, self).render(name, value, attrs)
