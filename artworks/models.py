# -*- coding: utf-8 -*-
from django.db.models import Q
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from base.models import BibliographicReference, GeospatialReference, Image
from creators.models import Creator


class Serie(models.Model):
    title = models.CharField(_(u'Title'), max_length=250)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)

    def __unicode__(self):
        return self.title


class Virgin(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    apparition_place = models.ForeignKey(GeospatialReference,
                                         verbose_name=_(u'apparition place'),
                                         blank=True, null=True)
    apparition_date = models.DateField(_(u'Apparition date'), blank=True,
                                       null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)
    # Migration
    fm_apparition_place = models.TextField(_(u'Filemaker apparition place'),
                                           blank=True, null=True)

    def __unicode__(self):
        return self.name


class ArtworkManager(models.Manager):

    def in_range(self, year_from, year_to):
        params = ((Q(creation_year_start__lte=year_from) &
                   Q(creation_year_end__gte=year_from)) |
                  (Q(creation_year_start__gte=year_from) &
                   Q(creation_year_end__lte=year_to)) |
                  (Q(creation_year_start__lte=year_from) &
                   Q(creation_year_end__gte=year_from)))
        artworks = Artwork.objects.filter(params)
        return artworks


class Artwork(models.Model):
    title = models.CharField(_(u'Title'), max_length=250)
    creation_year_start = models.IntegerField(_(u'Creation year beginning'),
                                              blank=True, null=True,
                                              max_length=4)
    creation_year_end = models.IntegerField(_(u'Creation year ending'),
                                            blank=True, null=True,
                                            max_length=4)
    inscription = models.TextField(_(u'Inscription'), blank=True, null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)
    original_place = models.ForeignKey(GeospatialReference,
                                       verbose_name=_(u"Original place"),
                                       related_name="original_places",
                                       blank=True, null=True)
    current_place = models.ForeignKey(GeospatialReference,
                                      verbose_name=_(u"Current place"),
                                      related_name="current_places",
                                      blank=True, null=True)
    virgins = models.ManyToManyField(Virgin, verbose_name=_(u'virgins'),
                                     through='ArtworkVirgin',
                                     blank=True, null=True)
    images = models.ManyToManyField(Image, verbose_name=_(u'images'),
                                    blank=True, null=True)
    references = models.ManyToManyField(BibliographicReference,
                                        through='ArtworkBibliography',
                                        verbose_name=_(u'references'),
                                        blank=True, null=True)
    size = models.CharField(_(u'Size'), max_length=150, blank=True, null=True)
    inventory = models.CharField(_(u'Inventory number'), max_length=150,
                                 blank=True, null=True)
    serie = models.ForeignKey(Serie, verbose_name=_(u'serie'),
                              blank=True, null=True)
    input_date = models.DateTimeField(_(u'Input date'), auto_now_add=True,
                                      blank=True, null=True)
    creators = models.ManyToManyField(Creator, verbose_name=_(u"Creators"),
                                      blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    # Migration
    fm_original_place = models.TextField(_(u'Filemaker original place'),
                                         blank=True, null=True)
    fm_current_place = models.TextField(_(u'Filemaker current place'),
                                        blank=True, null=True)
    fm_inventory = models.TextField(_(u'Filemaker inventory number'),
                                    blank=True, null=True)
    fm_descriptors = models.TextField(_(u'Filemaker descriptors'),
                                      blank=True, null=True)

    objects = ArtworkManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('artworks.views.artworks_record', [str(self.id)])


class ArtworkVirgin(models.Model):
    artwork = models.ForeignKey(Artwork, verbose_name=_(u'artwork'))
    virgin = models.ForeignKey(Virgin, verbose_name=_(u'virgin'))
    episode = models.CharField(_(u'Episode'), max_length=200, blank=True,
                               null=True)
    main_theme = models.NullBooleanField(_(u'Main theme'), max_length=200,
                                         blank=True, null=True)
    miraculous = models.NullBooleanField(_(u'Miraculous'), blank=True,
                                         null=True)
    ethnic = models.CharField(_(u'Ethnic'), max_length=200, blank=True,
                              null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)

    def __unicode__(self):
        return _(u"%s in %s") % (self.virgin.name, self.artwork.title)


class ArtworkBibliography(models.Model):
    artwork = models.ForeignKey(Artwork, verbose_name=_(u'artwork'))
    bibliography = models.ForeignKey(BibliographicReference,
        verbose_name=_(u'bibliographic reference'))
    source = models.CharField(_(u'Source'), max_length=250, blank=True,
                              null=True)

    class Meta:
        verbose_name_plural = _(u'Artworks bibliographic references')

    def __unicode__(self):
        return _(u"%s @ %s") % (self.artwork.title, self.bibliography.title)
