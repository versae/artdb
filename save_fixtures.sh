#!/bin/bash

./manage.py dumpdata --format=xml --indent=4 auth > base/fixtures/auth.xml
./manage.py dumpdata --format=xml --indent=4 base > base/fixtures/data.xml
./manage.py dumpdata --format=xml --indent=4 django_descriptors > base/fixtures/descriptors.xml
./manage.py dumpdata --format=xml --indent=4 creators > creators/fixtures/data.xml
./manage.py dumpdata --format=xml --indent=4 artworks > artworks/fixtures/data.xml
