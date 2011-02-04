"""
Management command that allows to translate specific apps and projects
isolated from each other to prevent "monolithic" translation catalogues.

For Pinax we need to take care of two special locations:

- Pinax Apps (PINAX_ROOT/apps)
- Projects (PINAX_ROOT/projects)

Both will be ignored when running this management command.
"""
from django.core.management.commands import makemessages


class Command(makemessages.Command):
    help = ("Runs over the entire source tree of the current directory and "
        "pulls out all strings marked for translation. It creates (or "
        "updates) a message file in the conf/locale (in the django tree) or "
        "locale directory (for project and application), but ignores the "
        "paths apps/* and projects/* by default.")
    
    def handle(self, *args, **options):
        if not options.get("ignore_patterns"):
            options["ignore_patterns"] = ["apps/*", "projects*"]
        super(Command, self).handle(*args, **options)
