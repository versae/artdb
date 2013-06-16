#!/bin/bash
# In case of fail, apply the next patch
# https://code.djangoproject.com/attachment/ticket/16778/postgis-adapter.patch
./manage.py loaddata backups/auth.json
./manage.py loaddata backups/base.json
./manage.py loaddata backups/creators.json
./manage.py loaddata backups/artworks.json
./manage.py loaddata backups/django_descriptors.json
