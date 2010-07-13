# -*- coding: utf-8 -*-
from datetime import datetime

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from django_descriptors.admin import DescribedItemInline
from django_extensions.admin import AutocompleteAdmin

from artworks.admin import ArtworkCreatorInline
from creators.models import Creator


class CreatorBibliographyInline(admin.TabularInline):
    model = Creator.references.through
    extra = 1
    raw_id_fields = ('creator', 'bibliography')


class CreatorAdmin(AutocompleteAdmin):

    inlines = (ArtworkCreatorInline, CreatorBibliographyInline,
               DescribedItemInline)
    fieldsets = (
            (None, {
                'fields': ('name', 'gender',
                           'birth_year', 'fm_birth_place', 'birth_place',
                           'death_year', 'fm_death_place', 'death_place',
                           'school',
                           'activity_start_year', 'activity_end_year',
                           'fm_descriptors'),
            }),
            (_(u'More info'), {
                'classes': ('collapse', ),
                'fields': ('masters', 'images', 'fm_bibliography',
                           'notes'),
            }),
    )
    readonly_fields = ('fm_birth_place', 'fm_death_place',
                       'fm_bibliography', 'fm_descriptors')
    exclude = ('user', 'references')
    search_fields = ('name', 'school__name', 'birth_place__title',
                     'death_place__title')
    related_search_fields = {
        'birth_place': ('title', 'address'),
        'death_place': ('title', 'address'),
        'school': ('name', 'start_year', 'end_year'),
        'masters': ('name', 'birth_year', 'death_year'),
        'images': ('url', 'image'),
        'references': ('url', 'title', 'isbn'),
    }
    list_display = ('name', 'gender', 'life', 'activity', 'artworks', 'school',
                    'user', 'input_date')
    list_filter = ('user', 'input_date')

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

    def life(self, obj):
        if obj.birth_year and obj.death_year:
            return u"%s-%s" % (obj.birth_year, obj.death_year)
        elif obj.birth_year and not obj.death_year:
            return u"%s~" % obj.birth_year
        elif not obj.birth_year and obj.death_year:
            return u"~%s" % obj.death_year
        else:
            return u""
    life.short_description = _(u"Life")

    def activity(self, obj):
        if obj.activity_start_year and obj.activity_end_year:
            return u"%s-%s" % (obj.activity_start_year, obj.activity_end_year)
        elif obj.activity_start_year and not obj.activity_end_year:
            return u"%s~" % obj.activity_start_year
        elif not obj.activity_start_year and obj.activity_end_year:
            return u"~%s" % obj.activity_end_year
        else:
            return u""
    activity.short_description = _(u"Activity period")

    def artworks(self, obj):
        artworks_num = obj.artwork_set.count()
        return artworks_num
    artworks.allow_tags = True
    artworks.short_description = _(u"# Artworks")


class SchoolAdmin(AutocompleteAdmin):

    fieldsets = (
            (None, {
                'fields': ('name', 'fm_place', 'place',
                           'start_year', 'end_year', 'affiliation', 'notes')
            }),
    )
    readonly_fields = ('fm_place', )
    search_fields = ('name', 'place__title')
    related_search_fields = {
        'place': ('title', 'address'),
    }
    list_display = ('name', 'place', 'activity', 'creators_num', 'artworks_num')

    def activity(self, obj):
        if obj.start_year and obj.end_year:
            return u"%s-%s" % (obj.start_year, obj.end_year)
        elif obj.start_year and not obj.end_year:
            return u"%s~" % obj.start_year
        elif not obj.start_year and obj.end_year:
            return u"~%s" % obj.end_year
        else:
            return u""
    activity.short_description = _(u"Activity period")

    def creators_num(self, obj):
        creators = Creator.objects.filter(school=obj).count()
        return creators
    creators_num.short_description = _(u"# Creators")

    def artworks_num(self, obj):
        artworks_count = 0
        creators = Creator.objects.filter(school=obj)
        for creator in creators:
            artworks_count += creator.artwork_set.count()
        return artworks_count
    artworks_num.allow_tags = True
    artworks_num.short_description = _(u"# Artworks")


class WorkingHistoryAdmin(AutocompleteAdmin):

    fieldsets = (
            (None, {
                'fields': ('creator', 'fm_place', 'place',
                           'start_year', 'end_year', 'notes')
            }),
    )
    readonly_fields = ('fm_place', )
    search_fields = ('creator__name', 'place__title', 'start_year', 'end_year')
    related_search_fields = {
        'creator': ('name', 'birth_year', 'death_year'),
        'place': ('title', 'address'),
    }
    list_display = ('creator', 'place', 'activity')

    def activity(self, obj):
        if obj.start_year and obj.end_year:
            return u"%s-%s" % (obj.start_year, obj.end_year)
        elif obj.start_year and not obj.end_year:
            return u"%s~" % obj.start_year
        elif not obj.start_year and obj.end_year:
            return u"~%s" % obj.end_year
        else:
            return u""
    activity.short_description = _(u"Activity period")
