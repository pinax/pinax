# How to Contribute

There are many ways you can help contribute to Pinax and the various apps,
themes, and starter projects that it is made up of. Contributing code, writing
documentation, reporting bugs, as well as reading and providing feedback on
issues and pull requests, all are valid and necessary ways to
help.


## Watch the Videos

Each month we do a Pinax Hangout, where we talk about a Pinax app or starter project, and demo how it works. Watching the videos of our [previous Pinax Hangouts](https://www.youtube.com/channel/UCAPpNG85GLzUBwzYCjd4raQ) might be helpful to you and might make contributing to Pinax easier. Click on the Youtube description of each video and you will find an agenda of what was discussed during a particular Hangout.


## Questions/Help

When you have questions or need help it’s best to join our [Pinax project Slack channel](http://slack.pinaxproject.com) and ping us there. It is also valid to create an issue and add the `question` label to it but it will usually take us longer to answer a question that has been filed as an issue than to help you in Slack.

If you provide us with an example of a bug you ran into, something that isn’t working, something you don’t understand, we will be able to help you much faster. It is totally sufficient to take a screenshot and post it in Slack or add it to your GitHub issue.


## Reporting Bugs/ Requesting Features/ Making Pull Requests

If you’re not sure how to create an issue or make a pull request on GitHub, please read [this blog post](http://blog.pinaxproject.com/2015/11/10/guide-how-contribute-pinax/) for help. If things are still unclear or you run into any problems, please don’t hesitate to ping us in Slack.

When you create an issue, please make sure to assign the correct labels to it. See [this blog post]() for help.


## Committing Code

The great thing about using a distributed versioning control system like git
is that everyone becomes a committer. When other people write good patches
it makes it very easy to include their fixes/features and give them proper
credit for the work.

We recommend that you do all your work in a separate branch. When you
are ready to work on a bug or a new feature create yourself a new branch. The
reason why this is important is you can commit as often you like. When you are
ready you can merge in the change. Let's take a look at a common workflow:

    git checkout -b task-566
    ... fix and git commit often ...
    git push origin task-566

The reason we have created two new branches is to stay off of `master`.
Keeping master clean of only upstream changes makes yours and ours lives
easier. You can then send us a pull request for the fix/feature. Then we can
easily review it and merge it when ready.


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
someone else that might be reviewing the change. Lastly, if there is a
corresponding issue in Github issues for it, use the final line to provide
a message that will link the commit message to the issue and auto-close it
if appropriate.

    Add ability to travel back in time

    You need to be driving 88 miles per hour to generate 1.21 gigawatts of
    power to properly use this feature.

    Fixes #88


## Coding style

When writing code to be included in Pinax keep our style in mind:

* Follow [PEP8](http://www.python.org/dev/peps/pep-0008/) there are some
  cases where we do not follow PEP8. It is an excellent starting point.
* Follow [Django's coding style](http://docs.djangoproject.com/en/dev/internals/contributing/#coding-style)
  we're pretty much in agreement on Django style outlined there.

We would like to enforce a few more strict guides not outlined by PEP8 or
Django's coding style:

* PEP8 tries to keep line length at 80 characters. We follow it when we can,
  but not when it makes a line harder to read. It is okay to go a little bit
  over 80 characters if not breaking the line improves readability.
* Use double quotes not single quotes. Single quotes are allowed in cases
  where a double quote is needed in the string. This makes the code read
  cleaner in those cases.
* Docstrings always use three double quotes on a line of their own, so, for
  example, a single line docstring should take up three lines not one.
* Imports are grouped specifically and ordered alphabetically. This is shown
  in the example below.
* Always use `reverse` and never `@models.permalink`.
* Tuples should be reserved for positional data structures and not used
  where a list is more appropriate.
* URL patterns should use the `url()` function rather than a tuple.

Here is an example of these rules applied:

    # first set of imports are stdlib imports
    # non-from imports go first then from style import in their own group
    import csv

    # second set of imports are Django imports with contrib in their own
    # group.
    from django.core.urlresolvers import reverse
    from django.db import models
    from django.utils import timezone
    from django.utils.translation import ugettext_lazy as _

    from django.contrib.auth.models import User

    # third set of imports are external apps (if applicable)
    from tagging.fields import TagField

    # fourth set of imports are local apps
    from .fields import MarkupField


    class Task(models.Model):
        """
        A model for storing a task.
        """

        creator = models.ForeignKey(User)
        created = models.DateTimeField(default=timezone.now)
        modified = models.DateTimeField(default=timezone.now)

        objects = models.Manager()

        class Meta:
            verbose_name = _("task")
            verbose_name_plural = _("tasks")

        def __unicode__(self):
            return self.summary

        def save(self, **kwargs):
            self.modified = datetime.now()
            super(Task, self).save(**kwargs)

        def get_absolute_url(self):
            return reverse("task_detail", kwargs={"task_id": self.pk})

        # custom methods


    class TaskComment(models.Model):
        # ... you get the point ...
        pass


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


## Other Ways to Contribute/What We Need Help With

### Help Others!

If you would like to help others who are just starting to contribute to Pinax, you can do the following:

* Hang out in [Slack](http://slack.pinaxproject.com) and help answer questions!
* Watch the [Pinax repositories](https://github.com/pinax) for issues or pull request you could help with!
* When you encounter a bug/have an idea for a feature/encounter missing documentation that could easily be fixed, create `first-timers-only` issues like [this one](https://github.com/pinax/pinax/issues/102) for people wanting to make their first OSS contribution! If you need help creating this sort of issue, please ping @ossanna16 on GitHub or @anna in Slack.


### Contribute To The Community!

* Write blog posts [like these](http://blog.pinaxproject.com/section/how-tos/)!
* Host a [Pinax Hangout](https://www.youtube.com/channel/UCAPpNG85GLzUBwzYCjd4raQ)!
* Help us contribute to our existing documentation and write new documentation! You can find links to each app’s/starter project’s documentation in the README of the app/starter project.
* Write tutorials! If there’s an app or starter project you know well, write a tutorial and show others how to use it, what features it has, etc.


### Contribute Code!

* Write tests!
* If you have time to fix any of our GitHub issues (especially those labelled `up-for-grabs`) we would greatly appreciate your help!
* Create a new starter project which showcases how to use any of our Pinax apps (or a combination of them). This doesn’t have to be anything new or original. You could for example pick an existing website like Facebook and try to rebuild it with Pinax components.
* Write new Pinax apps! If while building your starter project you notice that an app is missing we would love for you to let us know about your idea or build the app yourself.








