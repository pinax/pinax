"""
Call this like ``python pinax/bin/create-venv-script.py``
it will refresh the pinax-boot.py script
"""
import os
import virtualenv

here = os.path.dirname(os.path.abspath(__file__))
script_name = os.path.join(here, 'pinax-boot.py')
extra_text = open(os.path.join(here,'_installer.py')).read()

def main():
    text = virtualenv.create_bootstrap_script(extra_text)
    if os.path.exists(script_name):
        f = open(script_name)
        cur_text = f.read()
        f.close()
    else:
        cur_text = ''
    print 'Updating %s' % script_name
    if cur_text == text:
        print 'No update'
    else:
        print 'Script changed; updating...'
        f = open(script_name, 'w')
        f.write(text)
        f.close()

if __name__ == '__main__':
    main()
