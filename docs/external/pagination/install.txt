Installing django-pagination
----------------------------

To install, first check out the latest version of the application from
subversion:

    svn co http://django-pagination.googlecode.com/svn/trunk django-pagination

Now, link the inner ``pagination`` project to your Python path:

    sudo ln -s `pwd`/pagination SITE_PACKAGES_DIR/pagination

If you don't know the location of your site packages directory, this hack might
do the trick for you:

    sudo ln -s `pwd`/pagination `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/pagination
    
Now it's installed.  Please see README.txt for information on how to use this
application in your projects.