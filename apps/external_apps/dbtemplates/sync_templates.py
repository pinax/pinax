"""This is just for backwards compatiblity"""
from optparse import OptionParser
from django.core.management import call_command

def main():
    parser = OptionParser()
    parser.add_option("-e", "--ext", dest="ext", action="store", type="string",
        help="file extension of the files you want to sync [default: %default]",
        default="html")
    parser.add_option("-f", "--force", action="store_true", dest="force",
        default=False, help="overwrite existing database templates")
    opts, args = parser.parse_args()

    call_command('sync_templates', **{'ext': opts.ext, 'force': opts.force})

if __name__ == "__main__":
    main()
