# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

from django_descriptors.models import Descriptor
from django_descriptors.admin import DescriptorAdmin

from artworks.models import Artwork, Virgin, Serie # ArtworkCreator
from artworks.admin import (ArtworkAdmin, SerieAdmin,
                            VirginAdmin) # ArtworkCreatorAdmin
from base.models import BibliographicReference, GeospatialReference, Image
from base.admin import (BibliographicReferenceAdmin, GeospatialReferenceAdmin,
                        ImageAdmin)
from creators.models import Creator, School, WorkingHistory
from creators.admin import CreatorAdmin, SchoolAdmin, WorkingHistoryAdmin


class AdminSite(admin.AdminSite):

    def has_permission(self, request):
        return request.user.is_superuser or request.user.is_staff


def setup_admin():
    admin_site.register(User, UserAdmin)
    admin_site.register(Group, admin.ModelAdmin)

    admin_site.register(Descriptor, DescriptorAdmin)

    admin_site.register(BibliographicReference, BibliographicReferenceAdmin)
    admin_site.register(GeospatialReference, GeospatialReferenceAdmin)
    admin_site.register(Image, ImageAdmin)

    admin_site.register(Serie, SerieAdmin)
    admin_site.register(Virgin, VirginAdmin)
    admin_site.register(Artwork, ArtworkAdmin)
    # admin_site.register(ArtworkCreator, ArtworkCreatorAdmin)

    admin_site.register(Creator, CreatorAdmin)
    admin_site.register(School, SchoolAdmin)
    admin_site.register(WorkingHistory, WorkingHistoryAdmin)

admin_site = AdminSite(name=settings.PROJECT_NAME)
setup_admin()
