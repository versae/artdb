# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'BibliographicReference.isbn'
        db.alter_column('base_bibliographicreference', 'isbn', self.gf('django.db.models.fields.IntegerField')(max_length=30, null=True, blank=True))

        # Changing field 'BibliographicReference.title'
        db.alter_column('base_bibliographicreference', 'title', self.gf('django.db.models.fields.TextField')())
    
    
    def backwards(self, orm):
        
        # Changing field 'BibliographicReference.isbn'
        db.alter_column('base_bibliographicreference', 'isbn', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True))

        # Changing field 'BibliographicReference.title'
        db.alter_column('base_bibliographicreference', 'title', self.gf('django.db.models.fields.CharField')(max_length=200))
    
    
    models = {
        'base.bibliographicreference': {
            'Meta': {'object_name': 'BibliographicReference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.IntegerField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'base.geospatialreference': {
            'Meta': {'object_name': 'GeospatialReference'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'})
        },
        'base.image': {
            'Meta': {'object_name': 'Image'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['base']
