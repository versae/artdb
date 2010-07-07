#!/bin/bash
./manage.py loaddata backups/auth.json
./manage.py loaddata backups/base.json
./manage.py loaddata backups/creators.json
./manage.py loaddata backups/artworks.json
./manage.py loaddata backups/django_descriptors.json
