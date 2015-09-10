Each of these will eventually link to a separate page for each app with:

* Description
* Maturity rating
* What starter projects use it
* What starter projects particularly showcase it
* How to add it to a project

# List of Apps

Apps that need to be assessed and triaged:

## [django-user-accounts](https://github.com/pinax/django-user-accounts)
django-user-accounts provides a Django project with a very extensible infrastructure for dealing with user accounts.
## [django-mailer](https://github.com/pinax/django-mailer)
django-mailer is a reusable Django app for queuing the sending of email.
## [django-waitinglist](https://github.com/pinax/django-waitinglist)
django-waitinglist is a Django waiting list app for running a private beta with cohorts support.
## [pinax-points](https://github.com/pinax/pinax-points)
pinax-points is a points, positions and levels app for Django.

pinax-points, formerly agon, provides the ability to track points on arbitrary objects in your system. The common case being User instances. It can additionally keep track of positions for these objects to produce leaderboards.

This code has mostly been pulled out of typewar and made slightly more generic to work well.
## [pinax-referrals](https://github.com/pinax/pinax-referrals)
pinax-referrals provides a Django site with referrals functionality.
## [pinax-ratings](https://github.com/pinax/pinax-ratings)
pinax-ratings is a ratings app for Django.
## [pinax-testimonials](https://github.com/pinax/pinax-testimonials)
pinax-testimonials is a testimonials app for Django.
## [pinax-blog](https://github.com/pinax/pinax-blog)
pinax-blog is a blog app for Django.
## [pinax-teams](https://github.com/pinax/pinax-teams)
pinax-teams is an app for Django sites that supports open, by invitation, and by application teams.
## [django-stripe-payments](https://github.com/pinax/django-stripe-payments)
django-stripe-payments is a payments Django app for Stripe.

This app allows you to process one off charges as well as signup users for recurring subscriptions managed by Stripe.
## [django-announcements](https://github.com/pinax/django-announcements)
django-announcements is a site-wide announcement reusable app for Django.

Some sites need the ability to broadcast an announcement to all of their users. django-announcements was created precisely for this reason. How you present the announcement is up to you as the site-developer. When working with announcements that are presented on the website one feature is that they are only viewed once. A session variable will hold which announcements an user has viewed and exclude that from their display. announcements supports two different types of filtering of announcements:

    site-wide (this can be presented to anonymous users)

    non site-wide (these can be used a strictly a mailing if so desired)

    members only (announcements are filtered based on the value of

        request.user)

## [pinax-notifications](https://github.com/pinax/pinax-notifications)
https://github.com/pinax/pinax-notifications
## [pinax-lms-activities](https://github.com/pinax/pinax-lms-activities)
pinax-lms-activities provides a framework and base learning activities for Pinax LMS.
## [pinax-forums](https://github.com/pinax/pinax-forums)
pinax-forums is an extensible forums app for Django and Pinax. It is focused on core forum functionality and hence is expected to be combined with other Pinax apps for broader features.

See pinax-project-forums for a full Django project incorporating numerous apps with the goal of providing an out of the box forums solution.
## [pinax-types](https://github.com/pinax/pinax-types)

## [django-email-confirmation (deprecated)](https://github.com/pinax/django-email-confirmation)
simple email confirmation for the Django web framework 

NOTE: this project has been superceded by https://github.com/pinax/django-user-accounts/ and is not longer active.
## [symposion](https://github.com/pinax/symposion)
symposion is a conference management solution from Eldarion. It was built with the generous support of the Python Software Foundation. See http://eldarion.com/symposion/ for commercial support, customization and hosting.
## [metron](https://github.com/pinax/metron)

## [phileo (soon to be pinax-likes)](https://github.com/pinax/phileo)

## [django-forms-bootstrap (deprecated?)](https://github.com/pinax/django-forms-bootstrap)

## [pinax-phone-confirmation](https://github.com/pinax/pinax-phone-confirmation)

## [django-bookmarks](https://github.com/pinax/django-bookmarks)

## [django-friends](https://github.com/pinax/django-friends)

## [django-flag](https://github.com/pinax/django-flag)

## [pinax-wiki](https://github.com/pinax/pinax-wiki)


Apps often follow the following template:

## [pinax-starter-app](https://github.com/pinax/pinax-starter-app)
