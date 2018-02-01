# Frequently Asked Questions

If you have any questions, please join our [Pinax Slack channel](http://slack.pinaxproject.com). Everyone is welcome!

## Which starter project should I start with?

If you want to build a new site with a combination of project-specific functionality and a few Pinax apps
then you probably want to start with either the **Zero** starter project (if you don't have users logging in to your site)
or the **Account** starter project (if you *do* have users logging in to your site).

## I've done the Quick Start and set up a project based on the Account starter project. Now what?

You can now start adding your own apps or existing Django apps (whether from Pinax or anywhere else).

## I already have an existing Django project. Can I still use Pinax?

Yes! A large component of Pinax is re-usable Django apps. Most apps make very few assumptions about what else
is in your project (although some assume you're using django-user-accounts for user account management).
In most cases you can just use an app in the Pinax ecosystem like you would any other Django app.

## How do we upgrade a site to a newer Pinax release?

Individual apps generally follow [semantic versioning](http://semver.org/) and often have an upgrade path.  So they should be upgradable.

If you want to use a starter project, or other collection of Pinax apps, and be able to follow a documented upgrade path, our
[Proposal for Pinax Distribution Versioning - pinax issue #84](https://github.com/pinax/pinax/issues/84) is required.
It provides coordinated releases and makes Pinax even more like a Linux distribution, in the way that e.g. Ubuntu
creates a coordinated release of an infrastructure along with a variety of applications.

## What editor/IDE/etc. do Pinax developers like to use?

One key to efficient coding is becoming comfortable and proficient with whatever system you use.
Our favorites these days include:

* [Visual Studio Code](https://code.visualstudio.com/)
* [PyCharm](https://www.jetbrains.com/pycharm/)
* [Sublime Text](https://www.sublimetext.com)

There is nothing Pinax-specific about these editor choices and we recommend that you use the text editor or IDE
you are most comfortable using and enjoy the most.
