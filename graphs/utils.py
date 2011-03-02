# -*-*- coding: utf-8 -*-
import codecs

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps
from django.utils.translation import gettext as _

from django_descriptors.models import Descriptor
from exhibit.utils import clean_years

from artworks.models import Artwork, Creator



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
            {nodeName:"%s", group:%s},""" % (artwork.title, artwork.creators.all()[0].id))
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
                                              descriptors_count*descriptors_count))
                cont += 1
    gexf.write(u"""
        ]
    }""")
    gexf.close()
    return filename


def export_gexf(year_from=1550, year_to=1575, min_descriptors_number=0):
    gexf = codecs.open("baroqueart.%s-%s.gexf" % (year_from, year_to), "w", "utf-8")
    gexf.write(u"""<?xml version="1.0" encoding="UTF-8"?> 
<gexf xmlns="http://www.gexf.net/1.1draft"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.gexf.net/1.1draft http://www.gexf.net/1.1draft/gexf.xsd"
    version="1.1"> 
    <graph mode="static" defaultedgetype="undirected">
        <attributes class="node">
            <attribute id="0" title="Creator" type="string"/>
        </attributes>
        <nodes>
    """)
    artworks = Artwork.objects.in_range(year_from,
                                        year_to).filter(creators__isnull=False).order_by("id")
    
    for artwork in artworks:
        gexf.write(u"""
            <node id="%s" label="%s" >
                <attvalues>
                    <attvalue for="0" value="%s"/>
                </attvalues>
            </node>""" % (artwork.id, artwork.title, artwork.creators.all()[0].name))
    gexf.write(u"""
        </nodes>
        <edges>""")
    links = []
    cont = 1
    for artwork1 in artworks:
        for artwork2 in artworks.filter(id__gt=artwork1.id):
            descriptors_count = Descriptor.objects.get_common(artwork1,
                                                        artwork2).count()
            if descriptors_count >= min_descriptors_number:
                gexf.write(u"""
<edge id="%s" source="%s" target="%s" type="undirected" weight="%s" />""" % (cont, artwork1.id,
                                              artwork2.id,
                                              descriptors_count))
                cont += 1
    gexf.write(u"""
        </edges>
    </graph>
</gexf>""")
    gexf.close()
    return u"baroqueart.%s-%s.gexf" % (year_from, year_to)


def export_desc_gexf(year_from=1550, year_to=1575, min_artworks_number=0):
    gexf = codecs.open("baroqueart.descriptors.%s-%s.gexf" % (year_from, year_to), "w", "utf-8")
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
                                        year_to).filter(creators__isnull=False).order_by("id")
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
    return u"baroqueart.descriptors.%s-%s.gexf" % (year_from, year_to)
