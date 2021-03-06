# -*- coding: utf-8 -*-
import csv

from datetime import datetime

from django.contrib.auth.models import User

from django_descriptors.models import DescribedItem, Descriptor

from base.models import BibliographicReference, GeospatialReference
from artworks.models import (Artwork, ArtworkVirgin, ArtworkBibliography,
                             Serie, Virgin)
from creators.models import Creator, School, WorkingHistory


def migrate_schools():
    """
    IDFM, nombre, Lugar, Fecha_Inicio, Fecha_Fin
    """
    print "Migrando Schools"
    School.objects.all().delete()
    reader = csv.reader(open('migrations/FMSchool.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        school = School()
        school.id = row[0]
        school.name = row[1]
        school.start_year = int(row[3] or 0)
        school.end_year = int(row[4] or 0)
        school.fm_place = row[2]
        school.save()


def migrate_virgins():
    """
    IDFM, nombre, Lugar_aparicion, Fecha_aparicion, Notas
    """
    print "Migrando Virgins"
    Virgin.objects.all().delete()
    reader = csv.reader(open('migrations/FMVirgin.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        virgin = Virgin()
        virgin.id = row[0]
        virgin.name = row[1]
        if row[3]:
            virgin.apparition_date = datetime.strptime(row[3],
                                                       "%d/%m/%Y").date()
        virgin.notes = row[4]
        virgin.fm_apparition_place = row[2]
        virgin.save()


def migrate_series():
    """
    IDFM, Nombre, notas
    """
    print "Migrando Series"
    Serie.objects.all().delete()
    reader = csv.reader(open('migrations/FMSerie.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        serie = Serie()
        serie.id = row[0]
        serie.title = row[1]
        serie.notes = row[2]
        serie.save()


def migrate_creators():
    """
    IDFM, Nombre, Género, Fecha_Nac, Lugar_Nac, Fecha_Muerte, Lugar_Muerte,
    IDSchool, Actividad_Inicio, Actividad_Fin, Notas, Bibliografía,
    Descriptores
    """
    print "Migrando Creators"
    admin_user = User.objects.get(id=1)
    Creator.objects.all().delete()
    reader = csv.reader(open('migrations/FMCreator.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        creator = Creator()
        creator.id = row[0]
        creator.name = row[1]
        if row[2]:
            creator.gender = (row[2] == "Hombre" and "M"
                              or row[2] == "Mujer" and "F")
        try:
            birth_year = int(row[3])
            creator.birth_year = birth_year
        except ValueError:
            pass
        try:
            death_year = int(row[5])
            creator.death_year = death_year
        except ValueError:
            pass
        try:
            fm_school_id = int(row[7])
            try:
                school = School.objects.get(id=fm_school_id)
                creator.school = school
            except School.DoesNotExist:
                pass
        except ValueError:
            pass
        try:
            activity_start_year = int(row[8])
            creator.activity_start_year = activity_start_year
        except ValueError:
            pass
        try:
            activity_end_year = int(row[9])
            creator.activity_end_year = activity_end_year
        except ValueError:
            pass
        creator.notes = row[10]
        creator.user = admin_user
        creator.fm_birth_place = row[4]
        creator.fm_death_place = row[6]
        creator.fm_bibliography = row[11]
        creator.fm_descriptors = row[12]
        creator.save()


def migrate_artworks():
    """
    IDFM, Titulo, Creation_year_start, Creation_year_end, inscription, notes,
    Original_place: (Nombre lugar + Pais + Provincia + Poblacion),
    Current_place: (Nombre lugar + Pais + Provincia + Poblacion),
    size, serie, NºInventario, Descriptores
    """
    print "Migrando Artworks"
    admin_user = User.objects.get(id=1)
    Artwork.objects.all().delete()
    reader = csv.reader(open('migrations/FMArtworks.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        artwork = Artwork()
        artwork.id = row[0]
        artwork.title = row[1]
        try:
            creation_year_start = int(row[2])
            artwork.creation_year_start = creation_year_start
        except ValueError:
            pass
        try:
            creation_year_end = int(row[3])
            artwork.creation_year_end = creation_year_end
        except ValueError:
            pass
        artwork.inscription = row[4]
        artwork.notes = row[5]
        artwork.size = row[14]
        try:
            fm_serie = int(row[15])
            try:
                serie = Serie.objects.get(id=fm_serie)
                artwork.serie = serie
            except Serie.DoesNotExist:
                pass
        except ValueError:
            pass
        artwork.inventory = row[16]
        artwork.user = admin_user
        artwork.fm_original_place = "%s, %s, %s, %s" % (row[6], row[7],
                                                         row[8], row[9])
        artwork.fm_current_place = "%s, %s, %s, %s" % (row[10], row[11],
                                                        row[12], row[13])
        artwork.fm_inventory = row[16]
        artwork.fm_descriptors = row[17]
        artwork.save()


def migrate_workinghistories():
    """
    IDFMAutor, Lugar, Fecha_Inicio, Fecha_Fin
    """
    print "Migrando Working histories"
    WorkingHistory.objects.all().delete()
    reader = csv.reader(open('migrations/FMWorkingHistory.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        workinghistory = WorkingHistory()
        try:
            creator_id = int(row[0])
            try:
                creator = Creator.objects.get(id=creator_id)
                workinghistory.creator = creator
            except School.DoesNotExist:
                pass
        except ValueError:
            pass
        try:
            start_year = int(row[2])
            workinghistory.start_year = start_year
        except ValueError:
            pass
        try:
            end_year = int(row[3])
            workinghistory.end_year = end_year
        except ValueError:
            pass
        workinghistory.fm_place = row[1]
        workinghistory.save()


def migrate_artworkcreators():
    """
    IDObra, IDAutor
    """
    print "Migrando ArtworkCreators"
    Artwork.objects.all()[0].creators.through.objects.all().delete()
    reader = csv.reader(open('migrations/FMArtworksCreator.csv'),
                        delimiter=',', quotechar='"')
    for row in reader:
        try:
            artwork_id = int(row[0])
            creator_id = int(row[1])
            try:
                creator = Creator.objects.get(id=creator_id)
                artwork = Artwork.objects.get(id=artwork_id)
                artwork.creators.add(creator)
                artwork.save()
            except (Creator.DoesNotExist, Artwork.DoesNotExist):
                pass
        except ValueError:
            pass


def migrate_masters():
    """
    IDDiscipulo, IDMaestro
    """
    print "Migrando Masters"
    Creator.objects.all()[0].masters.through.objects.all().delete()
    reader = csv.reader(open('migrations/FMMaestros.csv'),
                        delimiter=',', quotechar='"')
    for row in reader:
        try:
            creator_id = int(row[0])
            master_id = int(row[1])
            try:
                creator = Creator.objects.get(id=creator_id)
                master = Creator.objects.get(id=master_id)
                creator.masters.add(master)
                creator.save()
            except (Creator.DoesNotExist, Artwork.DoesNotExist):
                pass
        except ValueError:
            pass


def migrate_artworkvirgins():
    """
    IDObra, IDVirgen, episodio, Main_theme, Milagrosa, etnia
    """
    print "Migrando ArtworkVirgins"
    ArtworkVirgin.objects.all().delete()
    reader = csv.reader(open('migrations/FMArtowrkVirgin.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        artworkvirgin = ArtworkVirgin()
        try:
            artwork_id = int(row[0])
            virgin_id = int(row[1])
            try:
                artwork = Artwork.objects.get(id=artwork_id)
                virgin = Virgin.objects.get(id=virgin_id)
                artworkvirgin.artwork = artwork
                artworkvirgin.virgin = virgin
                artworkvirgin.episode = row[2]
                if row[3]:
                     artworkvirgin.main_theme = (row[3] == "Sí" and True
                                                 or row[3] == "No" and False)
                if row[4]:
                     artworkvirgin.miraculous = (row[4] == "Sí" and True
                                                 or row[4] == "No" and False)
                artworkvirgin.ethnic = row[5]
                artworkvirgin.save()
            except (Artwork.DoesNotExist, Virgin.DoesNotExist):
                pass
        except ValueError:
            pass


def migrate_all():
    print "Comenzando migración..."
    migrate_schools()
    print "- %s Schools" % School.objects.count()
    migrate_virgins()
    print "- %s Virgins" % Virgin.objects.count()
    migrate_series()
    print "- %s Series" % Serie.objects.count()
    migrate_creators()
    print "- %s Creators" % Creator.objects.count()
    migrate_workinghistories()
    print "- %s WorkingHistories" % WorkingHistory.objects.count()
    migrate_artworks()
    print "- %s Artworks" % Artwork.objects.count()
    migrate_artworkcreators()
    print "- %s relaciones entre Artworks y Creators" \
          % Artwork.objects.all()[0].creators.through.objects.count()
    migrate_masters()
    print "- %s relaciones entre Creators y sus maestros" \
          % Creator.objects.all()[0].masters.through.objects.count()
    migrate_artworkvirgins()
    print "- %s relaciones entre Artworks y Virgins" \
          % ArtworkVirgin.objects.count()
    print "Completado"


def update_artworks_decriptors():
    """
    artwotk_id:descriptor_id,descriptor_id,descriptor_id=value,
    """
    print "Actualizando descriptores de Artworks"
    admin_user = User.objects.get(id=1)
    f = open("migrations/artwork_descriptors.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'artworks': set(),
        'descriptors': set(),
    }
    while line:
        artwork_id, descriptors = line.strip().split(":")
        try:
            artwork = Artwork.objects.get(id=int(artwork_id))
            descriptor_tuples = descriptors.split(",")
            for descriptor_tuple in descriptor_tuples:
                if descriptor_tuple:
                    if "=" in descriptor_tuple:
                        descriptor_id, value = descriptor_tuple.split("=")
                    else:
                        descriptor_id, value = int(descriptor_tuple), u""
                    try:
                        descriptor = Descriptor.objects.get(id=descriptor_id)
                    except Descriptor.DoesNotExist:
                        errors['descriptors'].add(descriptor_id)
                    di = DescribedItem()
                    di.content_object = artwork
                    di.descriptor = descriptor
                    di.value = value[:250]
                    di.user = admin_user
                    di.save()
                    count += 1
        except Artwork.DoesNotExist:
            errors['artworks'].add(creator_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def update_creators_decriptors():
    """
    creator_id:descriptor_id,descriptor_id,descriptor_id=value,
    """
    print "Actualizando descriptores de Creators"
    admin_user = User.objects.get(id=1)
    f = open("migrations/creator_descriptors.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'creators': set(),
        'descriptors': set(),
    }
    while line:
        creator_id, descriptors = line.strip().split(":")
        try:
            creator = Creator.objects.get(id=int(creator_id))
            descriptor_tuples = descriptors.split(",")
            for descriptor_tuple in descriptor_tuples:
                if descriptor_tuple:
                    if "=" in descriptor_tuple:
                        descriptor_id, value = descriptor_tuple.split("=")
                    else:
                        descriptor_id, value = int(descriptor_tuple), u""
                    try:
                        descriptor = Descriptor.objects.get(id=descriptor_id)
                    except Descriptor.DoesNotExist:
                        errors['descriptors'].add(descriptor_id)
                    di = DescribedItem()
                    di.content_object = creator
                    di.descriptor = descriptor
                    di.value = value[:250]
                    di.user = admin_user
                    di.save()
                    count += 1
        except Creator.DoesNotExist:
            errors['creators'].add(creator_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def update_artwork_original_places_geos():
    """
    geos_id:artwork_id,artwork_id,
    """
    print "Actualizando referencias geoespaciales de Artworks__original_place"
    f = open("migrations/geospatialreference_artwork_original_places.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'geos': set(),
        'artworks': set(),
    }
    while line:
        geos_id, artworks = line.strip().split(":")
        try:
            geos = GeospatialReference.objects.get(id=int(geos_id))
            for artwork_id in artworks.split(","):
                if artwork_id:
                    artwork_id = int(artwork_id)
                    try:
                        artwork = Artwork.objects.get(id=artwork_id)
                    except Artwork.DoesNotExist:
                        errors['artworks'].add(artwork_id)
                    artwork.original_place = geos
                    artwork.save()
                    count += 1
        except GeospatialReference.DoesNotExist:
            errors['geos'].add(geos_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def update_artwork_current_places_geos():
    """
    geos_id:artwork_id,artwork_id,
    """
    print "Actualizando referencias geoespaciales de Artworks__current_place"
    f = open("migrations/geospatialreference_artwork_current_places.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'geos': set(),
        'artworks': set(),
    }
    while line:
        geos_id, artworks = line.strip().split(":")
        try:
            geos = GeospatialReference.objects.get(id=int(geos_id))
            for artwork_id in artworks.split(","):
                if artwork_id:
                    artwork_id = int(artwork_id)
                    try:
                        artwork = Artwork.objects.get(id=artwork_id)
                    except Artwork.DoesNotExist:
                        errors['artworks'].add(artwork_id)
                    artwork.current_place = geos
                    artwork.save()
                    count += 1
        except GeospatialReference.DoesNotExist:
            errors['geos'].add(geos_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def update_creator_death_places_geos():
    """
    geos_id:creator_id,creator_id,
    """
    print "Actualizando referencias geoespaciales de Creators__death_place"
    f = open("migrations/geospatialreference_creator_death_places.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'geos': set(),
        'creators': set(),
    }
    while line:
        geos_id, creators = line.strip().split(":")
        try:
            geos = GeospatialReference.objects.get(id=int(geos_id))
            for creator_id in creators.split(","):
                if creator_id:
                    creator_id = int(creator_id)
                    try:
                        creator = Creator.objects.get(id=creator_id)
                    except Creator.DoesNotExist:
                        errors['creators'].add(creator_id)
                    creator.death_place = geos
                    creator.save()
                    count += 1
        except GeospatialReference.DoesNotExist:
            errors['geos'].add(geos_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def update_creator_birth_places_geos():
    """
    geos_id:creator_id,creator_id,
    """
    print "Actualizando referencias geoespaciales de Creators__birth_place"
    f = open("migrations/geospatialreference_creator_birth_places.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'geos': set(),
        'creators': set(),
    }
    while line:
        geos_id, creators = line.strip().split(":")
        try:
            geos = GeospatialReference.objects.get(id=int(geos_id))
            for creator_id in creators.split(","):
                if creator_id:
                    creator_id = int(creator_id)
                    try:
                        creator = Creator.objects.get(id=creator_id)
                    except Creator.DoesNotExist:
                        errors['creators'].add(creator_id)
                    creator.birth_place = geos
                    creator.save()
                    count += 1
        except GeospatialReference.DoesNotExist:
            errors['geos'].add(geos_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def update_workinghistory_geos():
    """
    workinghistory_id:geos_id,
    """
    print "Actualizando referencias geoespaciales de WorkingHostory"
    f = open("migrations/workinghistory_geospatialreferences.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'workinghistories': set(),
        'geos': set(),
    }
    while line:
        workinghistory_id, geos_list = line.strip().split(":")
        try:
            workinghistory = WorkingHistory.objects.get(
                id=int(workinghistory_id)
            )
            for geos_id in geos_list.split(","):
                if geos_id:
                    geos_id = int(geos_id)
                    try:
                        geos = GeospatialReference.objects.get(id=geos_id)
                    except GeospatialReference.DoesNotExist:
                        errors['geos'].add(geos_id)
                    workinghistory.place = geos
                    workinghistory.save()
                    count += 1
        except WorkingHistory.DoesNotExist:
            errors['workinghistories'].add(workinghistory_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def update_all():
    print "Comenzando actualización..."
    c1, e1 = update_artworks_decriptors()
    print "- Relaciones: %s, Errores: %s" % (c1, e1)
    c2, e2 = update_creators_decriptors()
    print "- Relaciones: %s, Errores: %s" % (c2, e2)
    c3, e3 = update_artwork_original_places_geos()
    print "- Relaciones: %s, Errores: %s" % (c3, e3)
    c4, e4 = update_artwork_current_places_geos()
    print "- Relaciones: %s, Errores: %s" % (c4, e4)
    c5, e5 = update_creator_death_places_geos()
    print "- Relaciones: %s, Errores: %s" % (c5, e5)
    c6, e6 = update_creator_birth_places_geos()
    print "- Relaciones: %s, Errores: %s" % (c6, e6)
    c7, e7 = update_workinghistory_geos()
    print "- Relaciones: %s, Errores: %s" % (c7, e7)
    print "Completado (%s relaciones)" % reduce(lambda x, y: x + y,
                                                [c1, c2, c3, c4, c5, c6, c7])


def update_artwork_current_places_geos():
    """
    ID-Artwork: ID-Loc
    """
    print "Actualizando artworks__current_places con referencias geoespaciales"
    f = open("migrations/artwork_current_places_geospatialreference.list")
    line = f.readline()
    line_number = 1
    count = 0
    errors = {
        'artworks': set(),
        'geos': set(),
    }
    while line:
        artwork_id, geos_id = line.strip().split(":")
        try:
            artwork = Artwork.objects.get(id=int(artwork_id))
            try:
                geos = GeospatialReference.objects.get(id=int(geos_id))
                artwork.current_place = geos
                artwork.save()
                count += 1
            except GeospatialReference.DoesNotExist:
                errors['geos'].add(geos_id)
        except Artwork.DoesNotExist:
            errors['artworks'].add(artwork_id)
        line = f.readline()
        line_number += 1
    f.close()
    return count, errors


def migrate_biblio():
    """
    "ID-Biblio","Título","Autores","URL","ISBN","Notas"
    """
    print "Migrando Biblio"
    BibliographicReference.objects.all().delete()
    reader = csv.reader(open('migrations/FMBiblio.csv'), delimiter=',',
                        quotechar='"')
    for row in reader:
        biblio = BibliographicReference()
        biblio.id = row[0]
        biblio.title = row[1]
        if row[2]:
            biblio.authors = row[2]
        if row[3]:
            biblio.url = row[3]
        if row[4]:
            biblio.authors = row[4][:60]
        if row[5]:
            biblio.notes = row[5]
        biblio.save()


def migrate_artworkbibliography():
    """
    [ID-obra * ID-Biblio * "paginas..."]
    """
    print "Migrando ArtworkBibliography"
    ArtworkBibliography.objects.all().delete()
    reader = csv.reader(open('migrations/FMArtworkBibliography.csv'), delimiter='*',
                        quotechar='"')
    for row in reader:
        artwork_biblio = ArtworkBibliography()
        try:
            artwork_id = int(row[0])
            biblio_id = int(row[1])
            try:
                artwork = Artwork.objects.get(id=artwork_id)
                biblio = BibliographicReference.objects.get(id=biblio_id)
                artwork_biblio.artwork = artwork
                artwork_biblio.bibliography = biblio
                if len(row) > 2 and row[2]:
                    artwork_biblio.source = row[2][:250]
                artwork_biblio.save()
            except (Artwork.DoesNotExist, BibliographicReference.DoesNotExist):
                pass
        except ValueError:
            pass


def migrate_update():
    print "Comenzando migración..."
    migrate_biblio()
    print "- %s BibliographicReferences" % BibliographicReference.objects.count()
    migrate_artworkbibliography()
    print "- %s ArtworkBibliographies" % ArtworkBibliography.objects.count()
    print "Comenzando actualización..."
    c1, e1 = update_artwork_current_places_geos()
    print "- Relaciones: %s, Errores: %s" % (c1, e1)
    print "Completado (%s relaciones)" % reduce(lambda x, y: x + y,
                                                [c1, ])
