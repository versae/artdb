# -*- coding: utf-8 -*-
from django import forms
from django.core import urlresolvers
from django.contrib import admin
from django.utils.translation import ugettext as _

from django_extensions.admin import AutocompleteAdmin

from artworks.models import Artwork, ArtworkVirgin #, ArtworkCreator


class ArtworkInline(admin.TabularInline):
    model = Artwork
    extra = 0
    fieldsets = (
            (None, {
                'classes': ('collapse', ),
                'fields': ('title', 'creation_year_start',
                           'creation_year_end', 'size'),
            }),
            (_(u'Details'), {
                'classes': ('collapse', ),
                'fields': (),
            }),
    )

class ArtworkVirginInline(admin.TabularInline):
    model = ArtworkVirgin
    extra = 1
    fieldsets = (
            (None, {
                'classes': ('collapse', ),
                'fields': ('artwork', 'virgin', 'episode'),
            }),
            (_(u'Details'), {
                'classes': ('collapse', ),
                'fields': ('main_theme', 'miraculous', 'ethnic'),
            }),
    )
    raw_id_fields = ('artwork', )


class ArtworkCreatorInline(admin.StackedInline):
#    model = ArtworkCreator
    model = Artwork.creators.through
    extra = 1
#    raw_id_fields = ('artwork', 'creator')


class ArtworkAdminForm(forms.ModelForm):

    class Meta:
        model = Artwork


class ArtworkAdmin(AutocompleteAdmin):

    form = ArtworkAdminForm
    inlines = (ArtworkVirginInline, )
#    inlines = (ArtworkCreatorInline, ArtworkVirginInline)
    fieldsets = (
            (None, {
                'fields': ('title', 'serie', 'creators', 'creation_year_start',
                           'creation_year_end', 'inscription',
                           'original_place', 'current_place'),
            }),
            (_(u'More info'), {
                'classes': ('collapse', ),
                'fields': ('size', 'images', 'references', 'notes'),
            }),
    )
    exclude = ('user', )
    search_fields = ('title', 'creation_year_start', 'creation_year_end',
                     'inscription', 'notes', 'size', 'serie__title')
    related_search_fields = {
        'serie': ('title', ),
        'creators': ('name', ),
        'original_place': ('title', 'address', 'description'),
        'current_place': ('title', 'address', 'description'),
        'images': ('url', 'image'),
        'references': ('url', 'title', 'isbn'),
    }
    list_display = ('title', 'creation_year', 'creators', 'inscription',
                    'notes', 'size')
#    raw_id_fields = ('images', )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def creation_year(self, obj):
        return u"%s-%s" % (obj.creation_year_start, obj.creation_year_end)
    creation_year.short_description = _(u"Creation")

    def creators(self, obj):
        artwork_creators = obj.creators.all()
        creators = []
        for artwork_creator in artwork_creators:
            admin_url = urlresolvers.reverse("admin:creators_creator_change",
                                             args=[artwork_creator.creator.id])
            creators.append("<a href='%s'>%s</a>" \
                            % (admin_url,
                               artwork_creator.creator.name))
        return " / ".join(creators)
    creators.allow_tags = True
    creators.short_description = _(u"Creators")


#class ArtworkCreatorAdmin(AutocompleteAdmin):

#    search_fields = ('artwork__title', 'artwork__creation_year_start',
#                     'artwork__creation_year_end', 'artwork__inscription',
#                     'artwork__notes', 'artwork__size', 'artwork__serie__title',
#                     'creator__name', 'creator__school__name',
#                     'creator__birth_place__title',
#                     'creator__death_place__title')
#    related_search_fields = {
#        'artwork': ('title', 'inscription', 'size'),
#        'creator': ('name', 'school__name'),
#    }
#    raw_id_fields = ('artwork', )
#    list_display = ('artwork', 'creator_link')

#    def creator_link(self, obj):
#        admin_url = urlresolvers.reverse("admin:creators_creator_change",
#                                         args=[obj.creator.id])
#        creator = "<a href='%s'>%s</a>" % (admin_url, obj.creator.name)
#        return creator
#    creator_link.allow_tags = True
#    creator_link.short_description = _(u"Creator")


class SerieAdmin(admin.ModelAdmin):

    inlines = (ArtworkInline, )
    search_fields = ('title', 'notes')
    list_display = ('title', 'artworks', 'notes')

    def artworks(self, obj):
        return obj.artwork_set.count()
    artworks.short_description = _(u"# Artworks")


class VirginAdmin(admin.ModelAdmin):

    inlines = (ArtworkVirginInline, )
    search_fields = ('name', 'apparition_place', 'apparition_date')
    list_display = ('name', 'apparition_place', 'artworks', 'apparition_date')

    def artworks(self, obj):
        return obj.artwork_set.count()
    artworks.short_description = _(u"# Artworks")
