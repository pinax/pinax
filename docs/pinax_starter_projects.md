# Getting Started

The `pinax/pinax-starter-projects` repo is available [here](https://github.com/pinax/pinax-starter-projects/).

Many of the starter projects are derivatives of each other `zero` is the parent of `account` among many
others). We leverage `git` and branching to manage the hierarchy. Each project template lives in it's
own branch and will branch from its natural parent.

All starter projects share a common method for getting started. It involves creating a virtual environment, installing Django, and running the `startproject` command with a URL to the template, followed by a few commands within your new project. Or even easier, you can use the `pinax`
command line utility.

## Getting Started

You might use `pyenv` instead.

```
pip install virtualenv
virtualenv mysiteenv
source mysiteenv/bin/activate
```

### Using the `pinax` command line utility

```
pip install pinax-cli
pinax projects  # list available project releases
pinax start <kind> <project_name>
```

If you are feeling adventurous you can install off latest development by passing
the `--dev` flag:

```
pinax start --dev <kind> <project_name>
```


### Manually

```
pip install Django
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/<PROJECT_BRANCH> mysite -n webpack.config.js -n PROJECT_README.md
```



### Get Going With Your New Project

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
    * [social-auth](starter_project_list.md#pinax-project-social-auth)
    * [wiki](starter_project_list.md#pinax-project-wiki)
      * [team-wiki](starter_project_list.md#pinax-project-team-wiki)
  * [blog](starter_project_list.md#pinax-project-blog)
  * [static](starter_project_list.md#pinax-project-static)
  * [waiting-list](starter_project_list.md#pinax-project-waiting-list)
* `social`
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
