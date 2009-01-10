#!/usr/bin/env python

import glob
import os
import optparse
import sys
import shutil
import re

EXCLUDED_PATTERNS = ('.svn',)
DEFAULT_PINAX_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
PINAX_ROOT_RE = re.compile(r'PINAX_ROOT\s*=.*$', re.M)

def get_projects_dir(pinax_root):
    return os.path.join(pinax_root, 'projects')

def get_projects(pinax_root):
    return glob.glob(os.path.join(get_projects_dir(pinax_root), '*'))

def ignore_copytree(directory, contents):
    ignored_contents = []
    for content in contents:
        ignore_content = False
        for pattern in EXCLUDED_PATTERNS:
            if pattern in os.path.join(directory, content):
                ignore_content = True
                break
        if ignore_content:
            ignored_contents.append(content)
    return (directory, ignored_contents)

def update_settings(pinax_root, path, old_name, new_name):
    settings_file = open(path, 'r')
    settings = settings_file.read()
    settings_file.close()
    settings = settings.replace(old_name, new_name)
    settings = PINAX_ROOT_RE.sub("PINAX_ROOT = '%s'" % (pinax_root,), settings)
    settings_file = open(path, 'w')
    settings_file.write(settings)
    settings_file.close()

def rename_deploy_files(path, old_name, new_name):
    for deploy_file in glob.glob(old_name + '*'):
        shutil.move(deploy_file, deploy_file.replace(old_name, new_name))

def main(pinax_root, project_name, destination, verbose=True):
    if os.path.exists(destination):
        print "Files already exist at this path: %s" % (destination,)
        sys.exit(1)
    user_project_name = os.path.basename(destination)
    if project_name in map(os.path.basename, get_projects(options.pinax_root)):
        source = os.path.join(get_projects_dir(pinax_root), project_name)
    else:
        if not os.path.exists(project_name):
            print "Project template does not exist at this path: %s" % (
                project_name,)
            sys.exit(1)
        source = project_name
    if verbose:
        print "Copying your project to its new location"
    shutil.copytree(source, destination, ignore=ignore_copytree)
    if verbose:
        print "Updating settings.py for your new project"
    update_settings(pinax_root, os.path.join(destination, 'settings.py'),
        project_name, user_project_name)
    if verbose:
        print "Renaming your deployment files"
    rename_deploy_files(os.path.join(destination, 'deploy'), project_name,
        user_project_name)
    if verbose:
        print "Finished cloning your project, now you may enjoy Pinax!"

if __name__ == "__main__":
    usage = ("Usage: %prog [options] PROJECT_NAME DESTINATION\n\n(Note that " +
        "PROJECT_NAME may be a path to a project template of your own)")
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-r', '--pinax-root', dest='pinax_root',
        default=DEFAULT_PINAX_ROOT,
        help='the directory that can be used ')
    parser.add_option('-l', '--list-projects', dest='list_projects',
        action='store_true',
        help='lists the projects that are available on this system')
    parser.add_option('-v', '--verbose', dest='verbose',
        action='store_false', default=True,
        help='enables verbose output')
    (options, args) = parser.parse_args()
    
    if options.list_projects:
        print "Available Projects"
        print "------------------"
        sys.path.insert(0, get_projects_dir(options.pinax_root))
        for project in map(os.path.basename, get_projects(options.pinax_root)):
            print "%s:" % (project,)
            about = getattr(__import__(project), '__about__', '')
            for line in about.strip().splitlines():
                print '    %s' % (line,)
            print ''
        sys.exit(0)

    if len(args) < 2:
        parser.print_usage()
        sys.exit(1)
    
    main(options.pinax_root, args[0], args[1], verbose=options.verbose)