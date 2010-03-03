#!/bin/bash
# Your user mus be postgres superuser

echo "Dropping database"
dropdb artdb
echo "Creating database"
createdb -T template_postgis --owner=artdb artdb

if (( $? )) ; then
  echo "Unable to create database (check django or shell are not running and try again)."
  exit 1
fi
./manage.py syncdb --noinput

# echo "Enter password for 'admin' user:"
# ./manage.py createsuperuser --username=admin --email=artdb@cvltvre.com

echo "Installing fixtures"
./manage.py loaddata base/fixtures/auth.xml
./manage.py loaddata base/fixtures/data.xml
./manage.py loaddata creators/fixtures/data.xml
./manage.py loaddata artworks/fixtures/data.xml
# ./manage.py migrate

if (( $? )) ; then
  echo "Unable to create the new schemaNo (syncdb)."
  exit 1
fi
