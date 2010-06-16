# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
from django.utils.translation import gettext as _


class Image(models.Model):
    title = models.CharField(_(u'Title'), max_length=200)
    image = models.ImageField(_(u'Image'), upload_to='images',
                              blank=True, null=True)
    url = models.URLField(_(u'URL'), verify_exists=False,
                          blank=True, null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.url or self.image.url)


class BibliographicReference(models.Model):
    title = models.TextField(_(u'Title'))
    url = models.URLField(_(u'URL'), verify_exists=False, blank=True,
                          null=True)
    isbn = models.CharField(_(u'ISBN'), max_length=30, blank=True,
                               null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)

    def __unicode__(self):
        return self.title


class GeospatialReference(models.Model):
    title = models.CharField(_('Title'), max_length=250, unique=True)
    address = models.CharField(_('Address'), max_length=250, blank=True,
                               null=True)
    geometry = models.MultiPolygonField(_('Geometry'), blank=True, null=True)
    point = models.PointField(_('Point'), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    date = models.DateTimeField(_('Date'), auto_now=True)

    objects = models.GeoManager()

    def __unicode__(self):
        if self.address:
            return u"%s (%s)" % (self.title, self.address)
        else:
            return u"%s" % self.title

    def save(self, *args, **kwargs):
        if (self.geometry and self.point
            and not self.geometry.contains(self.point)):
            self.point = self.geometry.point_on_surface
        super(GeospatialReference, self).save(*args, **kwargs)
