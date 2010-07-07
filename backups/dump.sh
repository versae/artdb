#!/bin/bash
./manage.py dumpdata --format=json --indent=4 auth > backups/auth.json
./manage.py dumpdata --format=json --indent=4 base > backups/base.json
./manage.py dumpdata --format=json --indent=4 django_descriptors > backups/django_descriptors.json
./manage.py dumpdata --format=json --indent=4 creators > backups/creators.json
./manage.py dumpdata --format=json --indent=4 artworks > backups/artworks.json
