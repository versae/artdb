# -*- coding: utf-8 -*-
from datetime import datetime

from django import forms
from django.core import urlresolvers
from django.contrib import admin
from django.utils.translation import ugettext as _

from django_descriptors.admin import DescribedItemInline
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
    raw_id_fields = ('artwork', 'virgin')


class ArtworkCreatorInline(admin.StackedInline):
#    model = ArtworkCreator
    model = Artwork.creators.through
    extra = 1
    raw_id_fields = ('artwork', 'creator')


class ArtworkAdminForm(forms.ModelForm):

    class Meta:
        model = Artwork


class ArtworkAdmin(AutocompleteAdmin):

    form = ArtworkAdminForm
    inlines = (ArtworkVirginInline, DescribedItemInline)
#    inlines = (ArtworkCreatorInline, ArtworkVirginInline)
    fieldsets = (
            (None, {
                'fields': ('title', 'serie', 'creators',
                           'creation_year_start', 'creation_year_end',
                           'fm_inventory', 'inventory', 'inscription',
                           'fm_original_place', 'original_place',
                           'fm_current_place', 'current_place',
                           'fm_descriptors'),
            }),
            (_(u'More info'), {
                'classes': ('collapse', ),
                'fields': ('size', 'images', 'references', 'notes'),
            }),
    )
    readonly_fields = ('fm_original_place', 'fm_current_place',
                       'fm_inventory', 'fm_descriptors')
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
    list_display = ('title', 'creation_year', 'creators_list',
                    'truncated_inscription', 'truncated_notes', 'size',
                    'user', 'input_date')
    list_filter = ('user', 'input_date')
#    raw_id_fields = ('images', )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.input_date = datetime.now()
        obj.save()

    # Needed in order to save user in DescribedItem
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, DescribedItemInline.model):
                instance.user = request.user
                instance.save()
        formset.save_m2m()

    def creation_year(self, obj):
        if obj.creation_year_start and obj.creation_year_end:
            return u"%s-%s" % (obj.creation_year_start, obj.creation_year_end)
        elif obj.creation_year_start and not obj.creation_year_end:
            return u"%s~" % obj.creation_year_start
        elif not obj.creation_year_start and obj.creation_year_end:
            return u"~%s" % obj.creation_year_end
        else:
            return u""
    creation_year.short_description = _(u"Creation")

    def creators_list(self, obj):
        artwork_creators = obj.creators.all()
        creators = []
        for artwork_creator in artwork_creators:
            admin_url = urlresolvers.reverse("admin:creators_creator_change",
                                             args=[artwork_creator.id])
            creators.append("<a href='%s'>%s</a>" \
                            % (admin_url,
                               artwork_creator.name))
        return " / ".join(creators)
    creators_list.allow_tags = True
    creators_list.short_description = _(u"Creators")

    def truncated_inscription(self, obj):
        return self.truncated(obj.inscription)
    truncated_inscription.short_description = _(u"Inscription")

    def truncated_notes(self, obj):
        return self.truncated(obj.notes)
    truncated_notes.short_description = _(u"Notes")

    def truncated(self, obj):
        if len(obj) > 150:
            return u"%s..." % obj[:150]
        else:
            return u""


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
    fieldsets = (
            (None, {
                'fields': ('title', 'notes'),
            }),
    )
    search_fields = ('title', 'notes')
    list_display = ('title', 'artworks', 'notes')

    def artworks(self, obj):
        return obj.artwork_set.count()
    artworks.short_description = _(u"# Artworks")


class VirginAdmin(AutocompleteAdmin):

    inlines = (ArtworkVirginInline, )
    fieldsets = (
            (None, {
                'fields': ('name',
                           'fm_apparition_place', 'apparition_place',
                           'apparition_date', 'notes'),
            }),
    )
    readonly_fields = ('fm_apparition_place', )
    search_fields = ('name', 'apparition_place', 'apparition_date')
    list_display = ('name', 'apparition_place', 'artworks', 'apparition_date')
    related_search_fields = {
        'apparition_place': ('title', 'address', 'description'),
    }

    def artworks(self, obj):
        return obj.artwork_set.count()
    artworks.short_description = _(u"# Artworks")
