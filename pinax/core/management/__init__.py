import os
import sys

import pinax


PINAX_COMMAND_DIR = os.path.join(
    os.path.dirname(pinax.__file__), "core", "management", "commands"
)


class CommandNotFound(Exception):
    pass


class CommandLoader(object):
    
    def __init__(self):
        self.command_dir = PINAX_COMMAND_DIR
        self.commands = {}
        self._load_commands()
    
    def _load_commands(self):
        for f in os.listdir(self.command_dir):
            if not f.startswith("_") and f.endswith(".py"):
                name = f[:-3]
                mod = "pinax.core.management.commands.%s" % name
                try:
                    __import__(mod)
                except:
                    self.commands[name] = sys.exc_info()
                else:
                    mod = sys.modules[mod]
                    self.commands[name] = mod.Command()
    
    def load(self, name):
        try:
            command = self.commands[name]
        except KeyError:
            raise CommandNotFound("Unable to find command '%s'" % name)
        else:
            if isinstance(command, tuple):
                # an exception occurred when importing the command so let's
                # re-raise it here
                raise command[0], command[1], command[2]
            return command


class CommandRunner(object):
    
    usage = "pinax-admin command [options] [args]"
    
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.loader = CommandLoader()
        self.loader.commands["help"] = self.help()
    
    def help(self):
        loader, usage = self.loader, self.usage
        # use BaseCommand for --version
        from pinax.core.management.base import BaseCommand
        class HelpCommand(BaseCommand):
            def handle(self, *args, **options):
                print "Usage: %s" % usage
                print
                print "Options:"
                print "  --version   show program's version number and exit"
                print "  -h, --help  show this help message and exit"
                print
                print "Available commands:"
                for command in loader.commands.keys():
                    print "  %s" % command
        return HelpCommand()
    
    def execute(self):
        argv = self.argv[:]
        try:
            command = self.argv[1]
        except IndexError:
            # display help if no arguments were given.
            command = "help"
            argv.extend(["help"])
        # special cases for pinax-admin itself
        if command in ["-h", "--help"]:
            argv.pop()
            command = "help"
            argv.extend(["help"])
        if command == "--version":
            argv.pop()
            command = "help"
            argv.extend(["help", "--version"])
        # load command and run it!
        try:
            self.loader.load(command).run_from_argv(argv)
        except CommandNotFound, e:
            sys.stderr.write("%s\n" % e.args[0])
            sys.exit(1)


def execute_from_command_line():
    """
    A simple method that runs a ManagementUtility.
    """
    runner = CommandRunner()
    runner.execute()
