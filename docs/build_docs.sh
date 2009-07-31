#!/bin/bash

rm -rf external/repos

mkdir -p external/repos
cd external/repos

echo "cloning django-email-confirmation"
git clone -q git://github.com/jezdez/django-email-confirmation.git
echo "cloning django-timezones"
git clone -q git://github.com/brosner/django-timezones.git
echo "cloning django-threadedcomments"
git clone -q git://github.com/ericflo/django-threadedcomments.git
echo "cloning django-ajax-validation"
git clone -q git://github.com/alex/django-ajax-validation.git
echo "cloning django-flag"
git clone -q git://github.com/pinax/django-flag.git
echo "cloning django-pagination"
git clone -q git://github.com/ericflo/django-pagination.git
echo "cloning django-oembed"
git clone -q git://github.com/ericflo/django-oembed.git
echo "cloning django-notification"
git clone -q git://github.com/brosner/django-notification.git
echo "cloning django-mailer"
git clone -q git://github.com/jtauber/django-mailer.git
echo "cloning django-dbtemplates"
git clone -q git://github.com/jezdez/django-dbtemplates.git
echo "cloning django-robots"
git clone -q git://github.com/jezdez/django-robots.git
echo "cloning django-announcements"
git clone -q git://github.com/pinax/django-announcements.git
echo "checking out django-messages"
svn checkout --quiet http://django-messages.googlecode.com/svn/trunk/ django-messages

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
rm -rf _build
make html