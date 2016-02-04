Each of these will eventually link to a separate page for each starter project with:

* Description
* What starter project it’s built on
* What apps it uses (and perhaps particularly showcases)

# List of Starter Projects

## Pinax-Project-Zero

This project lays the foundation for all other Pinax starter projects. It provides the project directory layout and Bootstrap-based theme.

```
pinax start zero mysite
```

## Pinax-Project-Account

In addition to what is provided by the "zero" project, this project provides thorough integration with django-user-accounts, adding comprehensive account management functionality. It is a foundation suitable for most sites that have user accounts.

```
pinax start account mysite
```

## Pinax-Project-SocialAuth

In addition to what is provided by the "account" project, this project
integrates with `python-social-auth` for Twitter, Facebook, and Google
authentication.

```
pinax start --dev social-auth mysite
```

## Pinax-Project-Blog

This project gets you off and running with a blog.

```
pinax start blog mysite
```

## Pinax-Project-Static

The purpose of this starter project is to provide a robust mocking and design tool.

```
pinax start static mysite
```

## Pinax-Project-Documents

Builds on the Accounts starter project to get you off and running with a document library built around [pinax-documents](https://github.com/pinax/pinax-documents).

```
pinax start documents mysite
```

## Pinax-Project-Wiki

This project is a demo starter project that provides a wiki for authenticated users.

```
pinax start wiki mysite
```

## Pinax-Project-Team-Wiki

This project is a starter project that has account management with profiles and teams and basic collaborative content.

```
pinax start team-wiki mysite
```

Additional starter projects:

* pinax-project-social
* pinax-project-waitinglist
* pinax-project-symposion
* pinax-project-lms
* pinax-project-forums
* pinax-project-teams


Some starter projects just demo an app or collection of apps. Some provide scaffolding during the development and testing of an app. Some are full-featured, out-of-the-box sites. Some lay the foundation for almost any custom Django site.
