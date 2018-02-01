# Pinax Starter Projects

The `pinax/pinax-starter-projects` repo is available [here](https://github.com/pinax/pinax-starter-projects/).

Many starter projects are derivatives of other projects (`zero` is the parent of `account` among many
others). We leverage `git` and branching to manage the hierarchy. Each project template lives in it's
own branch and branches from its natural parent.

All starter projects share a common method for getting started. It involves creating a virtual environment, installing Django, and running the `startproject` command with a URL to the template, followed by a few commands within your new project. Or even easier, you can use the `pinax`
command line utility.

## Getting Started

Refer to the Pinax Starter Project [Quick Start](quick_start.md) guide for simple steps to get started.

### Using the `pinax` command line utility

Since you've already installed `pinax-cli` as described in the [Quick Start](quick_start.md) guide,
you can experiment with the `pinax` command:

```shell
pinax projects  # list available project releases
pinax start <kind> <project_name>
```

If you are feeling adventurous you can install from the latest development branch by passing
the `--dev` flag:

```shell
pinax start --dev <kind> <project_name>
```

For the Pinax `documents`, `wiki`, `team-wiki`, and `social-auth` starter projects,
using the `--dev` option is the only way to create a project because
these do not yet have official releases. This is indicated by a lack of version number
next to the project:

```shell
$ pinax projects
Release Project
------- ---------------
  4.0.2 account
  4.0.2 blog
  2.0.2 company
        documents
        social-auth
  4.0.2 static
  4.0.2 stripe
        team-wiki
  3.0.2 waitinglist
        wiki
  4.0.2 zero
```


## Starter Project Inheritance

* [zero](#pinax-project-zero)
  * [account](#pinax-project-account)
    * [documents](#pinax-project-documents)
    * [social-auth](#pinax-project-social-auth)
    * [wiki](#pinax-project-wiki)
      * [team-wiki](#pinax-project-team-wiki)
  * [blog](#pinax-project-blog)
  * [static](#pinax-project-static)
  * [waiting-list](#pinax-project-waiting-list)
* social
* lms
* forums
* private-beta
* symposion


## Starter Project List

### Pinax-Project-Zero

This project lays the foundation for all other Pinax starter projects. It provides the project directory layout and Bootstrap-based theme.

```
pinax start zero mysite
```

### Pinax-Project-Account

In addition to what is provided by the "zero" project, this project provides thorough integration with django-user-accounts, adding comprehensive account management functionality. It is a foundation suitable for most sites that have user accounts.

```
pinax start account mysite
```

### Pinax-Project-SocialAuth

In addition to what is provided by the "account" project, this project
integrates with `python-social-auth` for Twitter, Facebook, and Google
authentication.

```
pinax start --dev social-auth mysite
```

### Pinax-Project-Blog

This project gets you off and running with a blog.

```
pinax start blog mysite
```

### Pinax-Project-Static

The purpose of this starter project is to provide a robust mocking and design tool.

```
pinax start static mysite
```

### Pinax-Project-Documents

Builds on the Accounts starter project to get you off and running with a document library built around [pinax-documents](https://github.com/pinax/pinax-documents).

```
pinax start documents mysite
```

### Pinax-Project-Wiki

This project is a demo starter project that provides a wiki for authenticated users.

```
pinax start wiki mysite
```

### Pinax-Project-Team-Wiki

This project is a starter project that has account management with profiles and teams and basic collaborative content.

```
pinax start team-wiki mysite
```

### Additional starter projects:

* pinax-project-social
* pinax-project-waitinglist
* pinax-project-symposion
* pinax-project-lms
* pinax-project-forums
* pinax-project-teams


## Starter Project Development

If you want to develop your own starter projects here is the workflow you should
follow:

1. Start with the branch you want to base your new project on.
2. `git co -b <name>`
3. Do the work on your project template
4. Test your project template by running `django-admin.py startproject --template=pinax-starter-projects test1 -n webpack.config.js -n PROJECT_README.md`
5. Once you are satisified with your testing, commit.
6. `git co master` and then update this `README.md` file with details about your new project
7. Update all descendent branches:

```shell
./update.sh
git push
```
