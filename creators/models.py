# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from base.models import BibliographicReference, Image, GeospatialReference


GENDERS = (
    ('M', _(u'Male')),
    ('F', _(u'Female')),
)


class School(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    place = models.ForeignKey(GeospatialReference, verbose_name=_(u'place'),
                              blank=True, null=True)
    start_year = models.IntegerField(_(u'Start year'), max_length=4,
                                     blank=True, null=True)
    end_year = models.IntegerField(_(u'End year'), max_length=4, blank=True,
                                   null=True)
    affiliation = models.CharField(_(u'Affiliation'), max_length=200,
                                   blank=True, null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)
    # Migration
    fm_place = models.TextField(_(u'Filemaker place'), blank=True, null=True)

    def __unicode__(self):
        return self.name


class Creator(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    gender = models.CharField(_(u'Gender'), max_length=1, choices=GENDERS,
                              blank=True, null=True)
    birth_year = models.IntegerField(_(u'Birth year'), max_length=4,
                                     blank=True, null=True)
    birth_place = models.ForeignKey(GeospatialReference,
                                    verbose_name=_(u'birth place'),
                                    related_name='creator_birthdate',
                                    blank=True, null=True)
    death_year = models.IntegerField(_(u'Death year'), max_length=4,
                                     blank=True, null=True)
    death_place = models.ForeignKey(GeospatialReference,
                                    verbose_name=_(u'death place'),
                                    related_name='creator_deathdate',
                                    blank=True, null=True)
    school = models.ForeignKey(School, verbose_name=_(u'school'),
                               related_name='creator_school',
                               blank=True, null=True)
    masters = models.ManyToManyField('self', verbose_name=_(u'masters'),
                                     symmetrical=False, blank=True, null=True)
    references = models.ManyToManyField(BibliographicReference,
                                        verbose_name=_(u"references"),
                                        blank=True, null=True)
    images = models.ManyToManyField(Image, verbose_name=_(u"images"),
                                    blank=True, null=True)
    activity_start_year = models.IntegerField(_(u'Activity start year'),
                                              max_length=4, blank=True,
                                              null=True)
    activity_end_year = models.IntegerField(_(u'Activity end year'),
                                             max_length=4, blank=True,
                                             null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)
    input_date = models.DateTimeField(_(u'Input date'), auto_now_add=True,
                                      blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    # Migration
    fm_birth_place = models.TextField(_(u'Filemaker birth place'),
                                      blank=True, null=True)
    fm_death_place = models.TextField(_(u'Filemaker death place'),
                                      blank=True, null=True)
    fm_bibliography = models.TextField(_(u'Filemaker bibliography'),
                                       blank=True, null=True)
    fm_descriptors = models.TextField(_(u'Filemaker descriptors'),
                                      blank=True, null=True)

    def __unicode__(self):
        return self.name


class WorkingHistory(models.Model):
    creator = models.ForeignKey(Creator, verbose_name=_(u'creator'))
    place = models.ForeignKey(GeospatialReference,
                              verbose_name=_(u'place'),
                              blank=True, null=True)
    start_year = models.IntegerField(_(u'Start year'), max_length=4,
                                     blank=True, null=True)
    end_year = models.IntegerField(_(u'End year'), max_length=4,
                                   blank=True, null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)
    # Migration
    fm_place = models.TextField(_(u'Filemaker place'),
                                blank=True, null=True)

    class Meta:
        verbose_name_plural = _(u'Working histories')

    def __unicode__(self):
        if self.place:
            return _(u"%s at %s") % (self.creator.name, self.place.title)
        else:
            return _(u"%s") % self.creator.name
