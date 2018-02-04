# How to Contribute

There are many ways you can help contribute to Pinax and the various apps,
themes, and starter projects that it is made up of. Contributing code, writing
documentation, reporting bugs, as well as reading and providing feedback on
issues and pull requests, all are valid and necessary ways to help.


## Watch the Videos

Each month we do a Pinax Hangout, where we talk about a Pinax app or starter project, and demo how it works. Watching the videos of our [previous Pinax Hangouts](https://www.youtube.com/channel/UCAPpNG85GLzUBwzYCjd4raQ) might be helpful to you and might make contributing to Pinax easier. Click on the Youtube description of each video and you will find an agenda of what was discussed during a particular Hangout.


## Questions/Help

When you have questions or need help it’s best to join our [Pinax project Slack channel](http://slack.pinaxproject.com) and ping us there. It is also valid to create an issue and add the `question` label to it but it will usually take us longer to answer a question that has been filed as an issue than to help you in Slack.

If you provide us with an example of a bug you ran into, something that isn’t working, something you don’t understand, we will be able to help you much faster. It is totally sufficient to take a screenshot and post it in Slack or add it to your GitHub issue.


## Reporting Bugs/ Requesting Features/ Making Pull Requests

If you’re not sure how to create an issue or make a pull request on GitHub, please read [this blog post](http://blog.pinaxproject.com/2015/11/10/guide-how-contribute-pinax/) for help. If things are still unclear or you run into any problems, please don’t hesitate to ping us in Slack.

When you create an issue, please make sure to assign the correct labels to it. See [this blog post](http://blog.pinaxproject.com/2016/01/11/first-timers-only-and-new-labels/) for help.


## Committing Code

We love thoughtful contributions from the Pinax community.
Developers like you improve Pinax apps all the time by filing issues
for bugs and feature requests, and even better by submitting pull requests.

One great thing about using a distributed versioning control system like git
is that anyone can become a contributor. You can clone a repository and work
on a new feature without fear of breaking the official release.

We recommend that you work on bug fixes or features in a new branch from "master".
First get the repository and create your own branch. If you are working
on pinax-ratings you'd type something like this:
 
```shell
mkdir pinax-ratings
git clone https://github.com/pinax/pinax-ratings.git pinax-ratings
cd pinax-ratings
git checkout master
git checkout -b my-new-branch
```

When your branch is ready for review, push it to GitHub and
open a pull request from your branch to master.

Here is a sample workflow of working on issue #27 with a cloned repository:

```shell
git checkout master
git checkout -b 27-frobnozz

# write code
git commit -a -m "Change the frobnozz"

# write code
git commit -a -m "Add tests"

git push origin 27-frobnozz
```

You are encouraged to add your name to the AUTHORS.md file in your pull
requests and receive credit for helping out.
Now go to Github to create a pull request for the fix/feature!
Once your pull request is created, Pinax maintainers are notified and
review your contributions.


### Writing Commit Messages

Writing a good commit message makes it simple for us to identify what your
commit does from a high-level. There are some basic guidelines we'd like to
ask you to follow.

A critical part is that you keep the **first** line as short and sweet
as possible. This line is important because when git shows commits and it has
limited space or a different formatting option is used the first line becomes
all someone might see. If your change isn't something non-trivial or there
reasoning behind the change is not obvious, then please write up an extended
message explaining the fix, your rationale, and anything else relevant for
someone reviewing the change. Lastly, if there is a
corresponding Github issue use the final line to provide
a message that will link the commit message to the issue and auto-close it
if appropriate. For instance, use `#27` to link to issue number 27:

```text
    Restore ability to travel back in time

    You need to be driving 88 miles per hour to generate 1.21 gigawatts of
    power to properly use this feature.

    Fixes #27
```


## Coding style

When writing code for Pinax apps, please keep our style in mind:

* Follow [PEP8](http://www.python.org/dev/peps/pep-0008/). There are some
  cases where we do not follow PEP8, but PEP8 is an excellent starting point.
* Follow [Django's coding style](http://docs.djangoproject.com/en/dev/internals/contributing/#coding-style)
  we're pretty much in agreement on Django style outlined there.

We enforce a few more strict guides not outlined by PEP8 or Django's coding style:

* PEP8 tries to keep line length at 80 characters. We follow it when we can,
  but not when it makes a line harder to read. It is okay to go a little bit
  over 80 characters if not breaking the line improves readability.
* Use double quotes ("double quotes") not single quotes ('single quotes').
  Single quotes are allowed in cases where a double quote is needed in the string.
  For example `title = 'Dwayne "The Rock" Johnson'`. We feel code reads cleaner
  in these situations.
* Docstrings always use three double quotes on a line of their own, so, for
  example, a single line docstring should take up three lines not one.
* Imports are grouped specifically and ordered alphabetically. This is shown
  in the example below.
* Always use `reverse` and never `@models.permalink`.
* Tuples should be reserved for positional data structures and not used
  where a list is more appropriate.
* URL patterns must use the `path()` and/or `url()` functions.
* When callable arguments require multiple lines, place each argument
  on a new line, indented four spaces from start of the function/method name.

Here is an example of these rules applied:

```python
# models.py

# first set of imports are stdlib imports
# non-from imports go first then from style import in their own group
import csv

# second set of imports are Django
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

# third set of imports are external apps (if applicable)
from pinax. import TagField

# fourth set of imports are local apps
from .fields import MarkupField
from .utils import frobnozz


class Task(models.Model):
    """
    A model for storing a task.
    """
    title = models.CharField(max_length=50)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("my_app:task_detail", args=[self.pk])

    def frobnozz_with_deconstrictulator(
            self,
            first_argument,
            second_argument,
            third_argument,
            fourth_argument):
        """
        Simulate frobnozzes after deconstriculation
        """
        # do some magic
```

This example shows use of `path()` and an acceptable line longer than 80 characters.

```
# urls.py

from django.urls import include, path

urlpatterns = [
    path("account/", include("account.urls")),
    path("tasks/<int:pk>/", TaskDetail.as_view(), name="task_view")
    path("tasks/<int:pk>/frobnozz/<int:pk>/wilco", TaskFrobnozz.as_view(), name="task_frobnozz")
    # more urls
]
```


## Testing

Pinax apps typically support several different versions of Python and several
different versions of Django. The supported combinations are specified in `tox.ini`
at the root of every Pinax app. Here is a sample `tox.ini` file from the Pinax 18.01 distribution:

```ini
[flake8]
ignore = E265,E501
max-line-length = 100
max-complexity = 10
exclude = **/*/migrations/*
inline-quotes = double

[isort]
multi_line_output=3
known_django=django
known_third_party=appconf,pinax
sections=FUTURE,STDLIB,DJANGO,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
skip_glob=**/*/migrations/*

[coverage:run]
source = pinax
omit = **/*/conf.py,**/*/tests/*,**/*/migrations/*
branch = true
data_file = .coverage

[coverage:report]
omit = **/*/conf.py,**/*/tests/*,**/*/migrations/*
exclude_lines =
    coverage: omit
show_missing = True

[tox]
envlist =
    checkqa,
    py27-dj{111}
    py34-dj{111,20}
    py35-dj{111,20}
    py36-dj{111,20}

[testenv]
passenv = CI CIRCLECI CIRCLE_*
deps =
    coverage
    codecov
    dj111: Django>=1.11,<1.12
    dj20: Django<2.1
    master: https://github.com/django/django/tarball/master

usedevelop = True
commands =
    coverage run setup.py test
    coverage report -m --skip-covered

[testenv:checkqa]
commands =
    flake8 pinax
    isort --recursive --check-only --diff pinax -sp tox.ini
deps =
    flake8 == 3.4.1
    flake8-quotes == 0.11.0
    isort == 4.2.15
```
    
The supported Python - Django combinations are specified in the `[tox] envlist=` section.

In order to test all supported Python/Django combinations we use `pyenv` and `detox` (`tox`).

### Installing `pyenv` and `detox`

First install `pyenv` according to the directions at https://github.com/yyuu/pyenv.
(Note you may need to install to a different shell profile configuration file, as
outlined in the installation directions.)

    $ brew install pyenv
    $ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
    $ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
    $ echo 'if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi' >> ~/.bash_profile
    $ exec $SHELL

Next install `detox`:

    $ pip install detox

### Installing Python versions

Using the Pinax app `tox.ini` file, determine what versions of Python are required for testing.
In our example above we support Python 2.7.x, 3.3.x, 3.4.x, and 3.5.x. Install the latest version
of each required Python <major>.<minor> release using `pyenv`:

    $ pyenv install 2.7.14
    $ pyenv install 3.4.7
    $ pyenv install 3.5.4
    $ pyenv install 3.6.4

Ensure these versions appear in the list of installed Python versions:

    $ pyenv versions
      3.6.4
      3.5.4
      3.4.7
      2.7.14

Now activate the versions required for your testing:

    $ pyenv local 3.6.4 3.5.4 3.4.7 2.7.14

and verify those versions are active (indicated by an asterisk next to the version number):

    $ pyenv versions
    * 3.6.4
    * 3.5.4
    * 3.4.7
    * 2.7.14

### Running tests

Finally, invoke `detox` in the same directory as `tox.ini`.

    $ detox

If your installation and setup worked, you should see something like this:

```shell
checkqa create: /Users/pinax/code/pinax-ratings/.tox/checkqa
py27-dj111 create: /Users/pinax/code/pinax-ratings/.tox/py27-dj111
py34-dj111 create: /Users/pinax/code/pinax-ratings/.tox/py34-dj111
py34-dj20 create: /Users/pinax/code/pinax-ratings/.tox/py34-dj20
py35-dj111 create: /Users/pinax/code/pinax-ratings/.tox/py35-dj111
py35-dj20 create: /Users/pinax/code/pinax-ratings/.tox/py35-dj20
py36-dj111 create: /Users/pinax/code/pinax-ratings/.tox/py36-dj111
py36-dj20 create: /Users/pinax/code/pinax-ratings/.tox/py36-dj20
...
```

Each test combination produces it's own output, so review errors carefully to understand
whether the problem lies with a general coding mistake or compatibility with a specific
version of Python and/or Django.

We encourage developers to test updated code before submitting a pull request.
Every pull request triggers our Travis continuous integration (CI) system,
which automatically tests the same Python/Django configurations using `tox.ini`.
A pull request which passes all tests in all configurations is a sign of quality
and attention to detail.


## Pull Requests

If you would like to add functionality or add a new feature, please submit an issue first to make sure it’s a direction we want to take.

Please keep your pull requests focused on one specific thing only. If you
have a number of contributions to make, then please send separate pull
requests. It is much easier on maintainers to receive small, well defined,
pull requests, than it is to have a single large one that batches up a
lot of unrelated commits.

If you ended up making multiple commits for one logical change, please
rebase into a single commit.

    git rebase -i HEAD~10  # where 10 is the number of commits back you need

This will pop up an editor with your commits and some instructions you want
to squash commits down by replacing 'pick' with 's' to have it combined with
the commit before it. You can squash multiple ones at the same time.

When you save and exit the text editor where you were squashing commits, git
will squash them down and then present you with another editor with commit
messages. Choose the one to apply to the squashed commit (or write a new
one entirely.) Save and exit will complete the rebase. Use a forced push to
your fork.

    git push -f

When you create a pull requests, which fixes an issue, please link the original issue in your pull request.
