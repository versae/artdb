# -*-*- coding: utf-8 -*-
import codecs
import csv
import nltk
import re

from StringIO import StringIO

from django.db.models import F, Q
from django.template.defaultfilters import force_escape as escape

from django_descriptors.models import Descriptor
from artworks.models import Artwork


# Taken from http://docs.python.org/library/csv.html#csv-examples
class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def export_nodes_edges(year_from=1550, year_to=1575, min_descriptors_number=0):
    filename = "data.%s-%s.json" % (year_from, year_to)
    gexf = codecs.open(filename, "w", "utf-8")
    gexf.write(u"""// Data: nodes and edges from %s to %s.
    var data = {
        nodes: [""" % (year_from, year_to))
    artworks = Artwork.objects.in_range(year_from,
                        year_to).filter(creators__isnull=False).order_by("id")
    for artwork in artworks:
        gexf.write(u"""
            {nodeName:"%s", group:%s},""" % (artwork.title,
                                             artwork.creators.all()[0].id))
    gexf.write(u"""
        ],
        links: [""")
    links = []
    cont = 1
    for artwork1 in artworks:
        for artwork2 in artworks.filter(id__gt=artwork1.id):
            descriptors_count = Descriptor.objects.get_common(artwork1,
                                                        artwork2).count()
            if descriptors_count >= min_descriptors_number:
                gexf.write(u"""
            {source:%s, target:%s, value:%s},""" % (artwork1.id,
                                      artwork2.id,
                                      descriptors_count * descriptors_count))
                cont += 1
    gexf.write(u"""
        ]
    }""")
    gexf.close()
    return filename


def export_gexf(year_from=1550, year_to=1575, min_descriptors_number=0,
                artwork_id_from=0, edge_id=0, with_original_location=None,
                with_current_location=None, prefix="",
                from_location=None, to_location=None):
    if with_original_location or with_current_location:
        location = "locations."
    else:
        location = ""
    filename = "%sbaroqueart.%s%s-%s.gexf" \
                % (prefix, location, year_from, year_to)
    artworks = Artwork.objects.in_range(year_from,
                                        year_to).exclude(creators=None)
    # Filtering by locations
    if with_original_location == True:
        # artworks = artworks.filter(original_place__isnull=False)
        artworks = artworks.exclude((Q(original_place__geometry=None)
                                    and Q(original_place__point=None)))
    elif with_original_location == False:
        artworks = artworks.filter(original_place=None)
    if with_current_location == True:
        # artworks = artworks.filter(current_place__isnull=False)
        artworks = artworks.exclude((Q(current_place__geometry=None)
                                    and Q(current_place__point=None)))
    elif with_current_location == False:
        artworks = artworks.filter(current_place=None)
    if from_location:
        artworks = artwork.objects.filter(
            Q(original_place__geometry__covers=from_location.geometry)
            or Q(original_place__geometry__coveredby=from_location.geometry)
            or Q(original_place__point__within=from_location.geometry)
        )
    if to_location:
        artworks = artwork.objects.filter(
            Q(current_place__geometry__covers=to_location.geometry)
            or Q(current_place__geometry__coveredby=to_location.geometry)
            or Q(current_place__point__within=to_location.geometry)
        )
    # Ordering by "id"
    artworks = artworks.order_by("id")
    if artwork_id_from:
        gexf = codecs.open(filename, "a+", "utf-8")
    else:
        gexf = codecs.open(filename, "w", "utf-8")
        gexf.write(u"""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.gexf.net/1.1draft http://www.gexf.net/1.1draft/gexf.xsd"
    version="1.1">
    <graph mode="static" defaultedgetype="undirected">
        <attributes class="node">
            <attribute id="0" title="Creator" type="string"/>
            <attribute id="1" title="CreatorId" type="integer"/>
            <attribute id="2" title="OriginalPlace" type="string"/>
            <attribute id="3" title="OriginalPlaceId" type="integer"/>
            <attribute id="4" title="OriginalPlaceLat" type="float"/>
            <attribute id="5" title="OriginalPlaceLon" type="float"/>
            <attribute id="6" title="CurrentPlace" type="string"/>
            <attribute id="7" title="CurrentPlaceId" type="integer"/>
            <attribute id="8" title="CurrentPlaceLat" type="float"/>
            <attribute id="9" title="CurrentPlaceLon" type="float"/>
        </attributes>
        <nodes>
    """)
        num_nodes = artworks.count()
        print("Printing %s nodes (max %s relationships)" % (num_nodes,
                                                            num_nodes ** 2))
        for artwork in artworks:
            start = ""
            if artwork.creation_year_start:
                start = u""" start="%s" """ % artwork.creation_year_start
            end = ""
            if artwork.creation_year_end:
                end = u""" end="%s" """ % artwork.creation_year_end
            creator = artwork.creators.all()[0]
            gexf.write(u"""
                <node id="%s" label='%s' >
                    <attvalues>
                        <attvalue for="0" value="%s"/>
                        <attvalue for="1" value="%s"/>""" \
                       % (artwork.id, escape(artwork.title),
                          escape(creator.name), creator.id))
            original_place_point = (artwork.original_place
                and (artwork.original_place.point
                     or (artwork.original_place.geometry
                         and artwork.original_place.geometry.point_on_surface)))
            if artwork.original_place and original_place_point:
                gexf.write(u"""
                        <attvalue for="2" value='%s'/>
                        <attvalue for="3" value='%s'/>
                        <attvalue for="4" value='%s'/>
                        <attvalue for="5" value='%s'/>""" \
                       % (escape(artwork.original_place.title),
                          artwork.original_place.id,
                          original_place_point.get_y(),
                          original_place_point.get_x()))
            current_place_point = (artwork.current_place
                and (artwork.current_place.point
                     or (artwork.current_place.geometry
                         and artwork.current_place.geometry.point_on_surface)))
            if artwork.current_place and current_place_point:
                gexf.write(u"""
                        <attvalue for="6" value='%s'/>
                        <attvalue for="7" value='%s'/>
                        <attvalue for="8" value='%s'/>
                        <attvalue for="9" value='%s'/>""" \
                       % (escape(artwork.current_place.title),
                          artwork.current_place.id,
                          current_place_point.get_y(),
                          current_place_point.get_x()))
            gexf.write(u"""
                    </attvalues>
                </node>""")
        gexf.write(u"""
            </nodes>
            <edges>""")
    cont = edge_id + 1
    artworks_qs1 = artworks.filter(id__gt=(artwork_id_from + 1))
    for artwork1 in artworks_qs1:
        artworks_qs2 = artworks.filter(id__gt=artwork1.id)
        for artwork2 in artworks_qs2:
            descriptors_count = Descriptor.objects.get_common(artwork1,
                                    artwork2).values("id").count()
            if descriptors_count >= min_descriptors_number:
                gexf.write(u"""
    <edge id="%s" source="%s" target="%s" type="undirected" weight="%s" />""" \
                           % (cont, artwork1.id, artwork2.id,
                              descriptors_count))
                cont += 1
            artwork2 = None
        artworks_qs2 = None
    gexf.write(u"""
        </edges>
    </graph>
</gexf>""")
    gexf.close()
    return filename


def export_desc_gexf(year_from=1550, year_to=1575, min_artworks_number=0):
    filename = "baroqueart.descriptors.%s-%s.gexf" % (year_from, year_to)
    gexf = codecs.open(filename, "w", "utf-8")
    gexf.write(u"""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.gexf.net/1.1draft http://www.gexf.net/1.1draft/gexf.xsd"
    version="1.1">
    <graph mode="static" defaultedgetype="undirected" start="%s" end="%s">
        <attributes class="node">
            <attribute id="0" title="Creator" type="string"/>
            <attribute id="1" title="Model" type="string"/>
        </attributes>
        <nodes>
    """ % (year_from, year_to))
    artworks = Artwork.objects.in_range(year_from,
                                        year_to).filter(creators__isnull=False)
    artworks = artworks.order_by("id")
    for artwork in artworks:
        start = ""
        if artwork.creation_year_start:
            start = u""" start="%s" """ % artwork.creation_year_start
        end = ""
        if artwork.creation_year_end:
            end = u""" end="%s" """ % artwork.creation_year_end
        gexf.write(u"""
            <node id="%s" label="%s" %s %s>
                <attvalues>
                    <attvalue for="0" value="%s"/>
                    <attvalue for="1" value="Artwork"/>
                </attvalues>
            </node>""" % (artwork.id, artwork.title, start, end,
                          artwork.creators.all()[0].name))
    descriptors = Descriptor.objects.all()
    for descriptor in descriptors:
        gexf.write(u"""
            <node id="d-%s" label="%s" >
                <attvalues>
                    <attvalue for="1" value="Descriptor"/>
                </attvalues>
            </node>""" % (descriptor.id, descriptor.name))
    gexf.write(u"""
        </nodes>
        <edges>""")
    cont = 1
    for descriptor in descriptors:
        if descriptor.parent:
            gexf.write(u"""
<edge id="%s" source="d-%s" target="d-%s" type="directed" />""" \
                      % (cont, descriptor.id, descriptor.parent.id))
            cont += 1
    for artwork in artworks:
        descriptors = Descriptor.objects.get_for_object(artwork)
        for descriptor in descriptors:
            gexf.write(u"""
    <edge id="%s" source="d-%s" target="%s" type="undirected" />""" \
                      % (cont, descriptor.id, artwork.id))
            cont += 1
    gexf.write(u"""
        </edges>
    </graph>
</gexf>""")
    gexf.close()
    return filename


def export_jflowmap_csv(year_from=1550, year_to=1575,
                        original_grouping=[], current_grouping=[],
                        exclude_static=False, prefix=""):
    # mexico = GeospatialReference.objects.get(id=366)
    # peru = GeospatialReference.objects.get(id=408)
#    nodes_filename = "%sbaroqueart.nodes.%s%s-%s.csv" \
#                % (prefix, location, year_from, year_to)
#    flows_filename = "%sbaroqueart.flows.%s%s-%s.csv" \
#                % (prefix, location, year_from, year_to)
    # Making the query
    artworks = Artwork.objects.in_range(year_from,
                                        year_to).exclude(creators=None)
    artworks = artworks.exclude((Q(original_place__geometry=None)
                                and Q(original_place__point=None)))
    artworks = artworks.exclude((Q(current_place__geometry=None)
                                and Q(current_place__point=None)))
    if exclude_static:
        artworks = artworks.exclude(original_place=F('current_place'))
    # Helpers
    def get_point(place):
        return (place
                and (place.point
                     or (place.geometry and place.geometry.point_on_surface)))

    def are_georelated(place1, place2):
        p1 = get_point(place1)
        p2 = get_point(place2)
        g1 = place1.geometry
        g2 = place2.geometry
        return (
            (g1 and p2 and g1.contains(p2)) or
            (g2 and p1 and g2.contains(p1)) or
            (g1 and g2 and (g1.overlaps(g2) or g2.overlaps(g1)))
         )

    def get_original_related(place):
        for original_place in original_grouping:
            if are_georelated(place, original_place):
                return original_place
        return place

    def get_current_related(place):
        for current_place in current_grouping:
            if are_georelated(place, current_place):
                return current_place
        return place

    # Init nodes and flows
    nodes = {}
    ids = set()
    flows = {}
    for place in original_grouping + current_grouping:
        nodes[place.id] = place
        ids.add(place.id)
    for artwork in artworks:
        original_place = get_original_related(artwork.original_place)
        current_place = get_current_related(artwork.current_place)
        key = u"%s,%s" % (original_place.id, current_place.id)
        if key not in flows:
            flows[key] = 0
        flows[key] += 1
        nodes[original_place.id] = original_place
        nodes[current_place.id] = current_place
        ids.add(original_place.id)
        ids.add(current_place.id)
    # Printing
    print(u"Nodes:\n======")
    print(u"Code,Name,Lat,Lon")
    for node_id in ids:
        node = nodes[node_id]
        point = get_point(node)
        print(u'%s,"%s",%s,%s' % (node_id, escape(node.title),
                                  point.get_y(), point.get_x()))
    print(u"Flows:\n======")
    print(u"Origin,Dest,Baroque Paintings Migrations")
    for k, v in flows.items():
        origin, target = k.split(",")
        print(u"%s,%s,%s" % (origin, target, v))
    return nodes, ids, flows


def add_descriptors_csv(file_number):
    """
    Id,Label,Creator,OriginalPlace,OriginalPlaceId,OriginalPlaceLat,
    OriginalPlaceLon,CurrentPlace,CurrentPlaceId,CurrentPlaceLat,
    CurrentPlaceLon,Modularity Class
    """
    filename = "baroqueart.%s.csv" % file_number
    csv_filename = "baroqueart.%s.desc.csv" % file_number
    # CSV File
    reader = csv.reader(open(filename, "r"), delimiter=',', quotechar='"')
    csv_file = open(csv_filename, "w")
    writer = UnicodeWriter(csv_file)
    labels = ["Artwork ID", "Artwork Title", "Creator ID", "Creator Name",
              "Original Place ID", "Original Place Title", "Modularity Class",
              "Degree", "Weighted Degree", "Eccentricity",
              "Closeness Centrality", "Betweenness Centrality", "Authority",
              "Hub", "PageRank", "Component ID", "Clustering Coefficient",
              "Number of triangles", "Eigenvector Centrality",
              "Descriptors vector"]
    descriptors = Descriptor.objects.all().order_by("id").values("name", "id")
    for descriptor in descriptors:
        labels.append(u"%s (%s)" % (descriptor["name"], descriptor["id"]))
    writer.writerow(labels)
    # ARFF File
    arff_filename = "baroqueart.%s.arff" % file_number
    arff_file = codecs.open(arff_filename, "w", "utf-8")
    arff_file.write(u"""
%% 1. Title: BaroqueArt Section %s
%%
%% 2. Sources:
%%      (a) Creator: Javier de la Rosa <versae@gmail.com>
%%      (b) Date: May, 2011
%%
@RELATION baroqueart

@ATTRIBUTE artwork_id NUMERIC
@ATTRIBUTE artwork_title STRING
@ATTRIBUTE creator_id NUMERIC
@ATTRIBUTE creator_name STRING
@ATTRIBUTE original_place_id NUMERIC
@ATTRIBUTE original_place_title STRING
@ATTRIBUTE modularity_class STRING
@ATTRIBUTE modularity_class NUMERIC
@ATTRIBUTE degree NUMERIC
@ATTRIBUTE weighted_degree NUMERIC
@ATTRIBUTE eccentricity NUMERIC
@ATTRIBUTE closeness_centrality NUMERIC
@ATTRIBUTE betweenness_centrality NUMERIC
@ATTRIBUTE authority NUMERIC
@ATTRIBUTE hub NUMERIC
@ATTRIBUTE pagerank NUMERIC
@ATTRIBUTE component_id NUMERIC
@ATTRIBUTE clustering_coefficient NUMERIC
@ATTRIBUTE number_of_triangles NUMERIC
@ATTRIBUTE eigenvector_centrality NUMERIC
@ATTRIBUTE descriptors_vector NUMERIC
""" % file_number)
    for descriptor in descriptors:
        arff_file.write(u"""@ATTRIBUTE desc-%s {yes, no}\n""" % (descriptor["id"]))
    arff_file.write(u"""
@DATA
""")
    # Skip first line with labels
    reader.next()
    errors = {
        'artworks': set(),
    }
    for line in reader:
        artwork_id = int(line[0])
        modularity = float(line[2])
        degree = float(line[3])
        weighted_degree = float(line[4])
        eccentricity = float(line[5])
        closeness_centrality = float(line[6])
        betweenness_centrality = float(line[7])
        authority = float(line[8])
        hub = float(line[9])
        pagerank = float(line[10])
        component_id = float(line[11])
        clustering_coefficient = float(line[12])
        number_of_triangles = float(line[13])
        eigenvector_centrality = float(line[14])
        try:
            artwork = Artwork.objects.get(id=artwork_id)
            if artwork.original_place and artwork.original_place.point:
                original_place_title = artwork.original_place.title
                original_place_id = artwork.original_place.id
            else:
                original_place_title = ""
                original_place_id = ""
            descriptors = Descriptor.objects.get_for_object(artwork)
            descriptors = descriptors.order_by("id")
            descs = Descriptor.objects.count() * [0]
            for descriptor in descriptors:
                descs[descriptor.id - 1] = 1
            creator = artwork.creators.all()[0]
            writer.writerow([artwork.id, artwork.title,
                             creator.id, creator.name,
                             original_place_id, original_place_title,
                             modularity, degree, weighted_degree,
                             eccentricity, closeness_centrality,
                             betweenness_centrality, authority, hub, pagerank,
                             component_id, clustering_coefficient,
                             number_of_triangles, eigenvector_centrality,
                             int("".join(map(unicode, descs)), 2)] \
                             + descs)

            def unicode_str(s):
                if s != "?":
                    if isinstance(s, (str, unicode)):
                        return unicode(u"\"%s\"" % s)
                    else:
                        return unicode(s)
                return s

            arff_file.write(u",".join(map(unicode_str, [artwork.id,
                             artwork.title,
                             creator.id, creator.name,
                             original_place_id or "?",
                             original_place_title or "?",
                             modularity, modularity, degree, weighted_degree,
                             eccentricity, closeness_centrality,
                             betweenness_centrality, authority, hub, pagerank,
                             component_id, clustering_coefficient,
                             number_of_triangles, eigenvector_centrality,
                             int("".join(map(unicode, descs)), 2)]) \
                             + map(lambda x: ("no", "yes")[x], descs)) + "\n")
        except Artwork.DoesNotExist, e:
            errors.add(e)
    csv_file.close()
    arff_file.close()
    return errors


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    _slugify_strip_re = re.compile(r'[^\w\s-]')
    _slugify_hyphenate_re = re.compile(r'[-\s]+')
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub(' ', value)


def freq_dist_virgins():
    words = ["maría", "maría", "virgin", "virgen", "señora", "nuestra señora",
             "ntra. señora", "ntra señora", "señora"]
    stop_words = ["el", "de", "con", "la", "y", "del", "a", "los", "en", "of",
                  "the", "al", "las", "los", "por", "su", "una", "un", "uno",
                  "o", "and", "il", "m"]
    lookups = Q()
    for word in words:
        lookups |= Q(title__icontains=word)
    artworks = Artwork.objects.filter(lookups).values("title")
    titles = []
    for artwork in artworks:
        print artwork["title"]
        title_split = slugify(artwork["title"].replace("  ",
                                                       " ").strip()).split()
        title_split = filter(lambda x: x not in stop_words, title_split)
        print title_split
        titles += title_split
        print title_split
    freq_dist = nltk.FreqDist(titles)
    freq_dist.plot()
    return freq_dist


def freq_dist_saints():
    words = ["san", "santo", "ntro señor", "nuestro señor", "our sir",
             "ntro. señor"]
    exclude_words = []
    stop_words = ["el", "de", "con", "la", "y", "del", "a", "los", "en", "of",
                  "the", "al", "las", "los", "por", "su", "una", "un", "uno",
                  "o", "and", "il", "m"]
    lookups = Q()
    for word in words:
        lookups |= Q(title__icontains=word)
    exclusions = Q()
    for word in exclude_words:
        exclusions |= Q(title__icontains=word)
    artworks = Artwork.objects.in_range(1600, 1625) \
               .filter(lookups).exclude(exclusions).values("title")
    titles = []
    for artwork in artworks:
        print artwork["title"]
        title_split = slugify(artwork["title"].replace("  ",
                                                       " ").strip()).split()
        title_split = filter(lambda x: x not in stop_words, title_split)
        print title_split
        titles += title_split
        print title_split
    freq_dist = nltk.FreqDist(titles)
    freq_dist.plot()
    return freq_dist


def freq_dist_civil():
    descriptor_id = 153  # [ Objeto ] → Clasificación → Temática → Civil
    descriptor = Descriptor.objects.get(id=descriptor_id)
    words = []
    exclude_words = []
    stop_words = ["el", "de", "con", "la", "y", "del", "a", "los", "en", "of",
                  "the", "al", "las", "los", "por", "su", "una", "un", "uno",
                  "o", "and", "il", "m"]
    lookups = Q()
    for word in words:
        lookups |= Q(title__icontains=word)
    exclusions = Q()
    for word in exclude_words:
        exclusions |= Q(title__icontains=word)
    artworks = Artwork.objects.in_range(1700, 2000) \
               .filter(lookups).exclude(exclusions)
    titles = []
    for artwork in artworks:
        if descriptor in Descriptor.objects.get_for_object(artwork):
            title_split = slugify(artwork.title.replace("  ",
                                                        " ").strip()).split()
            title_split = filter(lambda x: x not in stop_words, title_split)
            titles += title_split
    freq_dist = nltk.FreqDist(titles)
    freq_dist.plot()
    return freq_dist


def freq_dist_saints_rose():
    stop_words = ["el", "de", "con", "la", "y", "del", "a", "los", "en", "of",
                  "the", "al", "las", "los", "por", "su", "una", "un", "uno",
                  "o", "and", "il", "m"]
    artworks = Artwork.objects.in_range(1600, 2000) \
            .filter((Q(title__icontains="santa") \
                     & Q(title__icontains="rosa")) \
                  | (Q(title__icontains="saint") \
                     & Q(title__icontains="rose"))) \
            .values("title")
    titles = []
    for artwork in artworks:
        print artwork["title"]
        title_split = slugify(artwork["title"].replace("  ",
                                                       " ").strip()).split()
        title_split = filter(lambda x: x not in stop_words, title_split)
        print title_split
        titles += title_split
    freq_dist = nltk.FreqDist(titles)
    freq_dist.plot()
    return freq_dist


def freq_modularity_class(file_number, min_freq=0):
    """
    Id,Label,Creator,OriginalPlace,OriginalPlaceId,OriginalPlaceLat,
    OriginalPlaceLon,CurrentPlace,CurrentPlaceId,CurrentPlaceLat,
    CurrentPlaceLon,Modularity Class
    """
    filename = "baroqueart.%s.csv" % file_number
    csv_filename = "baroqueart.%s.modularity.csv" % file_number
    stop_words = ["el", "de", "con", "la", "y", "del", "a", "los", "en", "of",
                  "the", "al", "las", "los", "por", "su", "una", "un", "uno",
                  "o", "and", "il", "m", "le", "se", "e"]
    # CSV File
    reader = csv.reader(open(filename, "r"), delimiter=',', quotechar='"')
    csv_file = open(csv_filename, "w")
    writer = UnicodeWriter(csv_file)
    labels = []
    descriptors = Descriptor.objects.all().order_by("id").values("name", "id")
    for descriptor in descriptors:
        labels.append(u"%s (%s)" % (descriptor["name"], descriptor["id"]))
    # Skip first line with labels
    reader.next()
    errors = {
        'artworks': set(),
    }
    modularity_dict = {}
    words = {
        "titles": set(),
        "descriptors": set(),
        "paths": set(),
    }
    for line in reader:
        artwork_id = int(line[0])
        modularity = float(line[2])
        if modularity not in modularity_dict:
            modularity_dict[modularity] = {"titles": [],
                                           "descriptors": [],
                                           "paths": [],
                                           "total": 0}
        try:
            artwork = Artwork.objects.get(id=artwork_id)
            title_split = slugify(artwork.title.replace("  ",
                                                        " ").strip()).split()
            title_split = filter(lambda x: x not in stop_words, title_split)
            modularity_dict[modularity]["titles"] += title_split
            words["titles"] = words["titles"].union(title_split)
            modularity_dict[modularity]["total"] += 1
            descriptors = Descriptor.objects.get_for_object(artwork)
            descriptors = descriptors.order_by("id")
            for descriptor in descriptors:
                name = descriptor.name
                name_split = slugify(name.replace("  ", " ").strip()).split()
                name_split = filter(lambda x: x not in stop_words, name_split)
                modularity_dict[modularity]["descriptors"] += name_split
                words["descriptors"] = words["descriptors"].union(name_split)
                modularity_dict[modularity]["total"] += len(name_split)
                path = descriptor.path
                path_split = slugify(path.replace("  ", " ").strip()).split()
                path_split = filter(lambda x: x not in stop_words, path_split)
                modularity_dict[modularity]["paths"] += path_split
                words["paths"] = words["paths"].union(path_split)
                modularity_dict[modularity]["total"] += len(path_split)
        except Artwork.DoesNotExist, e:
            errors.add(e)
    modularity_freqs = {}
    for key, value in modularity_dict.items():
        if key not in modularity_freqs:
            modularity_freqs[key] = {}
        modularity_freqs[key]["titles"] = nltk.FreqDist(value["titles"])
        descriptors = value["descriptors"]
        modularity_freqs[key]["descriptors"] = nltk.FreqDist(descriptors)
        modularity_freqs[key]["paths"] = nltk.FreqDist(value["paths"])
        modularity_freqs[key]["total"] = value["total"]
    dataset = {}
    for elto in ["titles", "descriptors", "paths"]:
        data = []
        columns = []
        labels = [("Modularity %s" % mod_class)
                  for (mod_class, value) in modularity_freqs.items()]
        writer.writerow([elto.capitalize()] + labels)
        for word in words[elto]:
            freqs = [freq_dict[elto][word]
                     for (mod_class, freq_dict) in modularity_freqs.items()]
            if sum(freqs) > min_freq:
                writer.writerow([word] + freqs)
                data.append(freqs)
                columns.append(word)
        dataset[elto] = {
            'data': zip(*data),
            'rows': labels,
            'columns': columns,
        }
    save_modularity_barchart(file_number, dataset)
    csv_file.close()
    return modularity_freqs


def save_modularity_barchart(file_number, dataset):
    import pylab as p
    from matplotlib.font_manager import FontProperties
    import matplotlib.text as text

    fontP = FontProperties()
    fontP.set_size('small')
    fig = p.figure(figsize=(24, 6))
    figure_id = 1
    colours = ["#219FC7", "#C77B21", "#C7213F", "#00FF7F", "#BDB76B",
               "#FF00FF", "#FF6A00", "#21C79F", "#528B8B", "#216AA6",
               "#21F9C7", "#C7B721", "#C7123F", "#00F7FF", "#BD7B6B",
               "#FF0F0F", "#FFA600", "#217C9F", "#52B88B", "#21A6A6"]
    colours.reverse()
    for elto, values in dataset.items():
        data = values["data"]
        col_labels = values["columns"]
        row_labels = values["rows"]
        ax = fig.add_subplot(1, 3, figure_id, autoscale_on=True)
        # See note below on the breakdown of this command
        rows_length = len(data)
        ind = p.arange(len(col_labels)) + 0.3
        width = 0.3
        yoff = p.array([0.0] * len(col_labels))  # the bottom values for stacked bar chart
        for row in xrange(rows_length):
            ax.bar(ind, data[row], width, align="center", bottom=yoff,
                   facecolor=colours[row])
            yoff = yoff + data[row]

        # Create a y label
        ax.set_ylabel('Frequencies')
        # Create a title, in italics
        ax.set_title('Frequency of words in %s' % elto, fontstyle='italic')
        # This sets the ticks on the x axis to be exactly where we put
        # the center of the bars.
        ax.set_xticks(ind)
        # Set the x tick labels to the group_labels defined above.
        ax.set_xticklabels(col_labels)
        ax.grid(True)
        ax.axhline(0, color='black', lw=2)
        # Legend
        if figure_id == 3:
            # Shink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            # Put a legend to the right of the current axis
            ax.legend(row_labels, loc='center left', bbox_to_anchor=(1, 0.5),
                      prop=fontP)
        for o in fig.findobj(text.Text):
            o.set_fontsize(10)
        fig.autofmt_xdate()
        figure_id += 1
    filename = "baroqueart.%s.frequencies.png" % file_number
    fig.savefig(filename)


def save_modularity_chart(file_name, col_labels, row_labels, data):
    from matplotlib.colors import colorConverter
    from pylab import (asarray, linspace, axes, array, bar,
                       ylabel, arange, yticks, xticks, title, table, savefig,
                       subplot, legend)
    # subplot(111)
    axes([0.2, 0.2, 0.7, 0.6])   # leave room below the axes for the table
    colLabels = col_labels
    rowLabels = row_labels

    # Get some pastel shades for the colours
    colours = get_colours(len(rowLabels))
    colours.reverse()
    rows = len(data)

    leg = legend(row_labels, 'best', shadow=False)

    ind = arange(len(colLabels)) + 0.3  # the x locations for the groups
    width = 0.3     # the width of the bars
    yoff = array([0.0] * len(colLabels))  # the bottom values for stacked bar chart
    for row in xrange(rows):
        bar(ind, data[row], width, color=colours[row])
        # Acumulative
        # bar(ind, data[row], width, bottom=yoff)
        # yoff = yoff + data[row]
    ylabel("Words")
    xticks([])
    title('Frequency of words in %s' % file_name)
    filename = "/tmp/baroqueart.%s.png" % file_name
    print filename
    savefig(filename)


# Some simple functions to generate colours.
def pastel(colour, weight=2.4):
    """ Convert colour into a nice pastel shade"""
    from matplotlib.colors import colorConverter
    from pylab import (asarray, linspace)

    rgb = asarray(colorConverter.to_rgb(colour))
    # scale colour
    maxc = max(rgb)
    if maxc < 1.0 and maxc > 0:
        # scale colour
        scale = 1.0 / maxc
        rgb = rgb * scale
    # now decrease saturation
    total = sum(rgb)
    slack = 0
    for x in rgb:
        slack += 1.0 - x
    # want to increase weight from total to weight
    # pick x s.t.  slack * x == weight - total
    # x = (weight - total) / slack
    x = (weight - total) / slack
    rgb = [c + (x * (1.0 - c)) for c in rgb]
    return rgb


def get_colours(n):
    """ Return n pastel colours. """
    from matplotlib.colors import colorConverter
    from pylab import (asarray, linspace)

    base = asarray([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    if n <= 3:
        return base[0:n]
    # how many new colours to we need to insert between
    # red and green and between green and blue?
    needed = (((n - 3) + 1) / 2, (n - 3) / 2)
    colours = []
    for start in (0, 1):
        for x in linspace(0, 1, needed[start] + 2):
            colours.append((base[start] * (1.0 - x)) +
                           (base[start + 1] * x))
    return [pastel(c) for c in colours[0:n]]
