import os
import sys
import pinax

from django.core.management import LaxOptionParser
from django.core.management.base import BaseCommand, handle_default_options

_commands = None

def load_command_class(package_name, name):
    """
    Given a command name and a package name, returns the Command class instance.
    All errors raised by the import process (ImportError, AttributeError) are
    allowed to propagate.
    """
    module_name = '%s.management.commands.%s' % (package_name, name)
    module = __import__(module_name)
    for part in module_name.split('.')[1:]:
        module = getattr(module, part)
    command = module.Command()
    # If we don't do the following two things, Django tries to import settings.
    command.__class__.can_import_settings = False
    command.__class__.validate = lambda *args, **kwargs: None
    return command

def find_commands(management_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.
    
    Returns an empty list if no commands are defined.
    """
    command_dir = os.path.join(management_dir, 'commands')
    try:
        return [f[:-3] for f in os.listdir(command_dir)
            if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []

def get_commands():
    """
    Returns a dictionary mapping command names to their callback packages.
    
    This works by looking for a management.commands package in pinax.core, and
    if a commands package exists, all commands in that package are registered.
    
    The dictionary is in the format {command_name: package_name}. Key-value
    pairs from this dictionary can then be used in calls to
    load_command_class(app_name, command_name)
    
    The dictionary is cached on the first call and reused on subsequent
    calls.
    """
    global _commands
    
    # If the commands are non-none, return them
    if _commands is not None:
        return _commands
    
    _commands = dict([(name, 'pinax.core') for name in
        find_commands(__path__[0])])

    # Now that we've built the command list, return it.
    return _commands

class ManagementUtility(object):
    """
    Encapsulates the logic of the pinax-admin utility.
    
    A ManagementUtility has a number of commands, which can be manipulated by
    editing the self.commands dictionary.
    """
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
    
    def main_help_text(self):
        """
        Returns the script's main help text, as a string.
        """
        usage = ['',
                "Type '%s help <subcommand>' for help on a specific subcommand."
                 % self.prog_name, '']
        usage.append('Available subcommands:')
        commands = get_commands().keys()
        commands.sort()
        for cmd in commands:
            usage.append('  %s' % cmd)
        return '\n'.join(usage)
    
    def fetch_command(self, subcommand):
        """
        Tries to fetch the given subcommand, printing a message with the
        appropriate command called from the command line if it can't be found.
        """
        commands = get_commands()
        if subcommand not in commands:
            sys.stderr.write('Unknown command: %r\nType %s help for usage.\n' %
                (subcommand, self.prog_name))
            sys.exit(1)
        package_name = commands[subcommand]
        if isinstance(package_name, BaseCommand):
            klass = package_name
        else:
            klass = load_command_class(package_name, subcommand)
        return klass

    def execute(self):
        """
        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.
        """
        parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
            version=pinax.get_version(),
            option_list=BaseCommand.option_list)
        try:
            options, args = parser.parse_args(self.argv)
            handle_default_options(options)
        except:
            pass
        
        try:
            subcommand = self.argv[1]
        except IndexError:
            sys.stderr.write("Type '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)
        
        if subcommand == 'help':
            if len(args) > 2:
                self.fetch_command(args[2]).print_help(self.prog_name, args[2])
            else:
                parser.print_lax_help()
                sys.stderr.write(self.main_help_text() + '\n')
                sys.exit(1)
        elif self.argv[1:] == ['--version']:
            pass
        elif self.argv[1:] in [['--help'], ['-h']]:
            parser.print_lax_help()
            sys.stderr.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)

def execute_from_command_line(argv=None):
    """
    A simple method that runs a ManagementUtility.
    """
    utility = ManagementUtility(argv)
    utility.execute()