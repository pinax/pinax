# Getting Started

The pinax/pinax-starter projects repo is available [here](https://github.com/pinax/pinax-starter-projects/).

All starter projects share a common method for getting started. It involves creating a virtual environment, installing Django, and running the `startproject` command with a URL to the template, followed by a few commands within your new project.

Many of the starter projects are derivatives of each
other ([pinax-starter-projects-zero](http://github.com/pinax/pinax-starter-projects-zero) is a
parent of [pinax-starter-projects-project](http://github.com/pinax/pinax-starter-projects-project)
among many others).

We leverage `git` and branching to manage the hierarchy.

Each project template will get a new branch and will branch from its natural
parent.


All starter projects share a common method for getting started. It involves
creating a virtualenv, installing Django, and running the `startproject` command
with a url to the template, followed by a few commands within your new project.

### Create a virtualenv

You might use `pyenv` instead.

```
pip install virtualenv
virtualenv mysiteenv
source mysiteenv/bin/activate
```


### Install Django and Start Project

#### Manually

```
pip install Django==1.8.4
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/<PROJECT_BRANCH> mysite -n webpack.config.js -n PROJECT_README.md
```

#### Using the `pinax` Client

```
pip install pinax-cli
pinax projects --start=<KIND> mysite
```


#### Get Going With Your New Project

```
cd mysite
chmod +x manage.py
pip install -r requirements.txt
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```

See each section below for the startproject url as well as any deviation from
these common notes.


Projects
----------

* [zero](starter_project_list.md#pinax-project-zero)
  * [account](starter_project_list.md#pinax-project-account)
    * [documents](starter_project_list.md#pinax-project-documents)
    * [wiki](starter_project_list.md#pinax-project-wiki)
      * [team-wiki](starter_project_list.md#pinax-project-team-wiki)
  * [blog](starter_project_list.md#pinax-project-blog)
  * [static](starter_project_list.md#pinax-project-static)
  * [waiting-list](starter_project_list.md#pinax-project-waiting-list)
* `social`
* `social-auth`
* `lms`
* `forums`
* `private-beta`
* `symposion`


Development
---------------

If you want to develop your own starter projects here is the workflow you should
follow:

1. Start with the branch you want to base your new project on.
2. `git co -b <name>`
3. Do the work on your project template
4. Test your project template by running `django-admin.py startproject --template=pinax-starter-projects test1 -n webpack.config.js -n PROJECT_README.md`
5. Once you are satisified with your testing, commit.
6. `git co master` and then update this `README.md` file with details about your new project
7. Update all descendent branches:

```
./update.sh
git push
```
