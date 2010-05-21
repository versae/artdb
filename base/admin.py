# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.gis.maps.google import GoogleMap
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from olwidget.admin import GeoModelAdmin
from olwidget.widgets import MapDisplay, InfoMap

from base.models import GeospatialReference
from base.widgets import GoogleImagesSearchInput, OlWidgetGoogleMapsSearch

GMAP = GoogleMap(key=settings.GOOGLE_MAPS_API_KEY)


class GeospatialReferenceAdminForm(forms.ModelForm):

    class Meta:
        model = GeospatialReference

    def __init__(self, *args, **kwargs):
        super(GeospatialReferenceAdminForm, self).__init__(*args, **kwargs)
        attrs = {
            'size': 68,
            'class': 'olwidgetgooglemapssearch olwidget_maps:geometry,point',
        }
        self.fields['address'].widget = OlWidgetGoogleMapsSearch(attrs=attrs)

    def clean_geometry(self):
        geometry = self.cleaned_data['geometry']
        try:
            if geometry:
                coords = geometry.point_on_surface.get_coords()
        except:
            raise forms.ValidationError(_("Areas have to be plain (with no intersections)."))
        return geometry


class GeospatialReferenceAdmin(GeoModelAdmin):

    class Media:
        js = ('http://openlayers.org/api/2.8/OpenLayers.js',
              'http://openstreetmap.org/openlayers/OpenStreetMap.js',
              '%solwidget/js/olwidget.js' % settings.MEDIA_URL,
              'http://maps.google.com/maps?file=api&v=2&key=%s&sensor=true' \
              % settings.GOOGLE_MAPS_API_KEY)
        css = {'all': ('%solwidget/css/olwidget.css' % settings.MEDIA_URL, )}

    form = GeospatialReferenceAdminForm
    verbose_name = _(u"References")
    ordering = ('title', )
    fieldsets = (
            (None, {
                'fields': ('title', 'address', 'geometry'),
            }),
            (_(u'More info'), {
                'classes': ('collapse', ),
                'fields': ('point', 'description'),
            }),
    )
    search_fields = ('title', 'address', 'description')
    list_display = ('title', 'address', 'ubication_map')
    list_per_page = 5
    # Does not work with GeometryCollection
    # list_map = ('geometry', )
    options = {
        'layers': ['google.hybrid', 'google.streets', 'google.physical',
                   'google.satellite', 'osm.mapnik', 'osm.osmarender',
                   've.road', 've.shaded', 've.aerial', 've.hybrid'],
        'map_options': {
            'controls': ['LayerSwitcher', 'Navigation', 'PanZoom',
                         'Attribution', 'Scale', 'ScaleLine'],
         },
         # 'geometry': ['point', 'polygon'],
         # 'is_collection': False,
    }
    # Does not work with GeometryCollection
    # Cluster points and regions
    # list_map_options = options
    # list_map_options.update({
    #     'cluster': True,
    #     'cluster_display': 'list',
    # })

    def ubication_map(self, obj):
        info = [u""]
        try:
            if obj.geometry:
                geo = obj.geometry
                coords = geo.point_on_surface.get_coords()
            elif obj.point:
                geo = obj.point
                coords = geo.get_coords()
            info = [(geo, "%s %s" % (_(u"On surface"), coords))]
        except:
            return u""
        options = {
            'layers': ['google.streets'],
            'map_div_Style': {'width': '300px', 'height': '200px'},
        }
        map_display = InfoMap(info, options)
        return mark_safe(map_display.render(obj.title, {}))
    ubication_map.short_description = _(u"Ubication")
    ubication_map.allow_tags = True


class BibliographicReferenceAdmin(admin.ModelAdmin):

    list_display = ('title', 'url', 'isbn')
    search_fields = ('title', 'url', 'isbn')


class ImageAdmin(admin.ModelAdmin):

    list_display = ('title', 'images', 'notes')
    search_fields = ('title', 'image', 'url', 'notes')
    # Intended for search in Google Images
    formfield_overrides = {
        models.URLField: {
            'widget': GoogleImagesSearchInput(attrs={'class': 'googleimagessearchinput',
                                                     'size': 70})},
    }

    def images(self, obj):
        output = u""
        if obj.url:
            output = "%s<img src=\"%s\"/>" % (output, obj.url)
        if obj.image:
            output = "%s<img src=\"%s\"/>" % (output, obj.image.url)
        return mark_safe(output)
    images.short_description = _(u"Images")
    images.allow_tags = True
