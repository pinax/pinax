Each of these will eventually link to a separate page for each starter project with:

* Description
* What starter project it’s built on
* What apps it uses (and perhaps particularly showcases)

# List of Starter Projects

## Pinax-Project-Zero

This project lays the foundation for all other Pinax starter projects. It provides the project directory layout and Bootstrap-based theme.

```
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/zero mysite -n webpack.config.js
```

## Pinax-Project-Account

In addition to what is provided by the "zero" project, this project provides thorough integration with django-user-accounts, adding comprehensive account management functionality. It is a foundation suitable for most sites that have user accounts.

```
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/account mysite -n webpack.config.js
```

## Pinax-Project-Blog

This project gets you off and running with a blog.

```
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/blog mysite -n webpack.config.js
```

## Pinax-Project-Static

The purpose of this starter project is to provide a robust mocking and design tool.

```
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/static mysite -n webpack.config.js
```

## Pinax-Project-Documents

Builds on the Accounts starter project to get you off and running with a document library built around [pinax-documents](https://github.com/pinax/pinax-documents).

```
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/documents mysite -n webpack.config.js
```

## Pinax-Project-Wiki

This project is a demo starter project that provides a wiki for authenticated users.

```
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/wiki mysite -n webpack.config.js
```

## Pinax-Project-Team-Wiki

This project is a starter project that has account management with profiles and teams and basic collaborative content.

```
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/team-wiki mysite -n webpack.config.js
```

Additional starter projects:

* pinax-project-social
* pinax-project-socialauth
* pinax-project-waitinglist
* pinax-project-privatebeta
* pinax-project-symposion
* pinax-project-lms
* pinax-project-forums
* pinax-project-teams


Some starter projects just demo an app or collection of apps. Some provide scaffolding during the development and testing of an app. Some are full-featured, out-of-the-box sites. Some lay the foundation for almost any custom Django site.
