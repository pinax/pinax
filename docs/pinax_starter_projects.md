# New Approach

One of the things that has become a bit of a maintenance nightmare, especially as we add additional projects is keeping all the repos up to date with when most of the changes apply to all of them (e.g. upgrade Django version).

The pinax/pinax-starter projects repo, which is available [here](https://github.com/pinax/pinax-starter-projects/blob/master/README.md), serves as an experiment as a new way of managing this.

We will leverage `git` and branching to manage the hierarchy. The `master` branch will remain purely for the README and perhaps other ancillary files. Each project template will get a new branch and will branch from its natural parent. The README will be maintained with a full list of the branches and thus the starter projects in the repo. We may at some point add remotes to push each branch to its own repo where the code will live at master, but that will be treated purely as mirrors of this repo.

# Getting Started

All starter projects share a common method for getting started. It involves creating a `virtualenv`, installing Django, and running the `startproject command with a url to the template, followed by a few commands within your new project.

```
pip install virtualenv
virtualenv mysiteenv
source mysiteenv/bin/activate
pip install Django==1.8.4
django-admin.py startproject --template=https://github.com/pinax/pinax-starter-projects/zipball/<PROJECT_BRANCH> mysite -n webpack.config.js
cd mysite
chmod +x manage.py
pip install -r requirements.txt
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```

# Development

If you want to develop your own starter projects here is the workflow you should follow:

1. Start with the branch you want to base your new project on.
2. `git co -b <name>`
3. Do the work on your project template.
4. Test your project template by running `django-admin.py startproject --template=pinax-starter-projects test1 -n webpack.config.js`
5. Once you are satisified with your testing, commit.
6. `git co master` and then update the `README.md` file with details about your new project.
7. Update all descendent branches:

```
(
 git co zero && git merge master --no-edit
 git co account && git merge zero --no-edit
 git co blog && git merge zero --no-edit
 git co static && git merge zero --no-edit
 git co documents && git merge account --no-edit
 git co wiki && git merge account --no-edit
 git co team-wiki && git merge wiki --no-edit
)
git push
```
