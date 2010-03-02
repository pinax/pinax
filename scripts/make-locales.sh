#!/bin/bash
here=`pwd`
cd ..

CMD="$1"

for dir in pinax pinax/apps/* pinax/projects/* pinax/projects/*/apps/*
do
  if [ -d "${dir}" ]
  then
    cd ${dir}
    echo "Making/updating locales of '${dir}'"
    mkdir -p locale
    # hardcode locales for now
    case $CMD in
      "make")
        for locale in ar bg bn bs ca cs cy da de el en es es_AR et eu fa fi fr fy_NL ga gl he hi hr hu is it ja ka km kn ko lt lv mk nl no pl pt pt_BR ro ru sk sl sq sr sr_Latn sv ta te th tr uk vi zh_CN zh_TW
        do
          pinax-admin makemessages -l ${locale} -e html,txt -d django
        done
        ;;
      "compile")
        django-admin.py compilemessages
        ;;
      *)
        ;;
    esac
    cd ${here}/..
  fi
done
#cd scripts # :)