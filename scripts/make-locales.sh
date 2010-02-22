#!/bin/bash
here=`pwd`
cd ..
for dir in pinax pinax/apps/* pinax/projects/* pinax/projects/*/apps/*
do
  if [ -d "${dir}" ]
  then
    cd ${dir}
    echo "Making/updating locales of '${dir}'"
    mkdir -p locale
    # hardcode locales for now (with the old list from 0.5.X days)
    for locale in en de es fr sv pt_BR he ar it
    do
      pinax-admin makemessages -l ${locale} -e html,txt -d django
    done
    django-admin.py compilemessages
    cd ${here}/..
  fi
done
#cd scripts # :)