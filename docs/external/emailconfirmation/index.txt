#########################
django-email-confirmation
#########################

This simple app is for cases where you don't want to require an email
address to signup on your website but you do still want to ask for an
email address and be able to confirm it for use in optional parts of
your website.

A user can have zero or more email addresses linked to them. The user
does not have to provide an email address on signup but, if they do,
they are emailed with a link they must click on to confirm that the
email address is theirs. A confirmation email can be resent at any
time.

What's on the trunk here should be usable but I welcome feedback on how
to make it better. The source contains a working project that shows all
the features of the app as well as providing useful code for your own
project (although Pinax is a more comprehensive example of how to use
django-email-confirmation).

This code is based in part on django-registration and is essentially
a replacement for it where your requirements are different.
