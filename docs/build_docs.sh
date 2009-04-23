#!/bin/bash

rm -rf .build
rm -rf external/repos

mkdir -p external/repos
cd external/repos

git clone git://github.com/pinax/django-email-confirmation.git
git clone git://github.com/brosner/django-timezones.git
git clone git://github.com/ericflo/django-threadedcomments.git
git clone git://github.com/alex/django-ajax-validation.git
git clone git://github.com/pinax/django-flag.git
git clone git://github.com/ericflo/django-pagination.git
git clone git://github.com/ericflo/django-oembed.git
git clone git://github.com/brosner/django-notification.git
git clone git://github.com/pinax/django-mailer.git
git clone git://github.com/jezdez/django-dbtemplates.git
git clone git://github.com/jezdez/django-robots.git
git clone git://github.com/pinax/django-announcements.git
svn checkout http://django-messages.googlecode.com/svn/trunk/ django-messages

cd ../
ln -s repos/django-email-confirmation/docs emailconfirmation
ln -s repos/django-timezones/docs timezones
ln -s repos/django-threadedcomments/docs threadedcomments
ln -s repos/django-ajax-validation/docs ajax-validation
ln -s repos/django-flag/docs flag
ln -s repos/django-pagination/docs pagination
ln -s repos/django-oembed/docs oembed
ln -s repos/django-notification/docs notification
ln -s repos/django-mailer/docs mailer
ln -s repos/django-dbtemplates/docs dbtemplates
ln -s repos/django-robots/docs robots
ln -s repos/django-announcements/docs announcements
ln -s repos/django-messages/docs messages

cd ../
make html