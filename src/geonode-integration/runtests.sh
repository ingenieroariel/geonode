#!/bin/bash

GEONODE_URL="http://localhost/"
GEOSERVER_URL="http://localhost:8001/geoserver-geonode-dev/"

# Activate the virtualenv
# How can we test if its already activated?
# Assumes that geonode and geonode_tests are next to each other
echo ">>>> Activating VirtualEnv"
source ../../bin/activate

# Run the tests
echo ">>>> Running GeoNode Integration Tests" 
python manage.py test "$@"
