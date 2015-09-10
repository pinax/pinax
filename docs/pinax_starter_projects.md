# Getting Started

The pinax/pinax-starter projects repo is available [here](https://github.com/pinax/pinax-starter-projects/blob/master/README.md).

All starter projects share a common method for getting started. It involves creating a virtual environment, installing Django, and running the `startproject` command with a URL to the template, followed by a few commands within your new project.

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

If you want to develop your own starter projects, here is the workflow you should follow:

1. Start with the branch you want to base your new project on.
2. `git checkout -b <name>`
3. Work on your project template.
4. Test your project template by running `django-admin.py startproject --template=pinax-starter-projects test1 -n webpack.config.js`
5. Once you are satisified with your testing, commit.
6. `git checkout master` and then update the `README.md` file with details about your new project.
7. Update all descendent branches:

```
(
 git checkout zero && git merge master --no-edit
 git checkout account && git merge zero --no-edit
 git checkout blog && git merge zero --no-edit
 git checkout static && git merge zero --no-edit
 git checkout documents && git merge account --no-edit
 git checkout wiki && git merge account --no-edit
 git checkout team-wiki && git merge wiki --no-edit
)
git push
```
