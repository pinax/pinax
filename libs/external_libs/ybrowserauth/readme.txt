Test Yahoo! Mail and Photos APIs using Browser-Based Authentication
Author: Jason Levitt
Date: January 20th, 2007

Test out Y! Photos and Y! Mail access using bbatest.py

What you need:

* You need write access to a web server on the public Internet (including the root directory)
* Python 2.3x or greater, and mod_python with Apache
* A username and password to a Yahoo! Photos account
* A username and password to a Yahoo! Mail account

Directions:

0. If you want to test the Y! Mail API, rename the bbatestMAIL.py file to
   bbatest.py. If you want to test the Y! Photos API, rename the
   bbatestPHOTOS.py file to bbatest.py.

1. Place the files ybrowserauth.py and bbatest.py into the same 
   directory on your web server. Make the file HTACCESS the
   ".htaccess" file for that directory. 
   Optionally, you may run the setup.py script to install the 
   ybrowserauth class in your Python installation by typing:
   "python setup.py install" on your command line.

2. Register your application by going here:
   https://developer.yahoo.com/wsregapp/index.php

   When you fill out the registration form, put your application path, e.g.
   http://www.yourdomain.com/dir/bbatest.py
   in the "Web Application URL" form field.
   Choose a radio button for either Yahoo! Mail or Photos, depending on
   which one you are testing.
   Place the special text file, as directed, in the root of www.yourdomain.com

3. Edit the file bbatest.py, adding the appid and secret to the variables indicated
   near the top of the file. 

4. Run your app! http://www.yourdomain.com/dir/bbatest.py

5. Click on the link and login using a Yahoo! username/password that has 
   a Yahoo! Photos account. Some key bbauth values will be displayed along
   with some raw XML (Y! Photos) or a list of Mail folders (Y! Mail) from your
   Y! Photos or Y! Mail account
================================================
