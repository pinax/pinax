def email_confirmed(sender, user, **kwargs):
    request = sender
    
    # mark user as active
    user = kwargs.get("email_address").user
    user.is_active = True
    user.save()
