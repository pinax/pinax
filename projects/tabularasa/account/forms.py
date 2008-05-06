from django import newforms as forms
from django.core.validators import alnum_re

from django.template.loader import render_to_string

from django.conf import settings
from django.core.mail import send_mail # @@@ eventually use django-mailer

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress

class LoginForm(forms.Form):
    
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())
    password = forms.CharField(label="Password", widget=forms.PasswordInput(render_value=False))
    
    user = None
    
    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValdidationError(u"This account is currently inactive.")
        else:
            raise forms.ValidationError(u"The username and/or password you specified are not correct.")
        return self.cleaned_data
    
    def login(self, request):
        if self.is_valid():
            login(request, self.user)
            request.user.message_set.create(message="Successfully logged in as %s." % self.user.username)
            return True
        return False


class SignupForm(forms.Form):
    
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label="Password (again)", widget=forms.PasswordInput(render_value=False))
    email = forms.EmailField(label="Email (optional)", required=False, widget=forms.TextInput())
    
    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(u"Usernames can only contain letters, numbers and underscores.")
        try:
            user = User.objects.get(username__exact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(u"This username is already taken. Please choose another.")
    
    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(u"You must type the same password each time.")
        return self.cleaned_data
    
    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        new_user = User.objects.create_user(username, email, password)
        if email:
            new_user.message_set.create(message="Confirmation email sent to %s" % email)
            EmailAddress.objects.add_email(new_user, email)
        return username, password # required for authenticate()


class UserForm(forms.Form):
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class AddEmailForm(UserForm):
    
    email = forms.EmailField(label="Email", required=True, widget=forms.TextInput(attrs={'size':'30'}))
    
    def clean_email(self):
        try:
            EmailAddress.objects.get(user=self.user, email=self.cleaned_data["email"])
        except EmailAddress.DoesNotExist:
            return self.cleaned_data["email"]
        raise forms.ValidationError(u"This email address already associated with this account.")
    
    def save(self):
        self.user.message_set.create(message="Confirmation email sent to %s" % self.cleaned_data["email"])
        return EmailAddress.objects.add_email(self.user, self.cleaned_data["email"])


class ChangePasswordForm(UserForm):
    
    oldpassword = forms.CharField(label="Current Password", widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label="New Password (again)", widget=forms.PasswordInput(render_value=False))
    
    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(u"Please type your current password.")
        return self.cleaned_data["oldpassword"]
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(u"You must type the same password each time.")
        return self.cleaned_data["password2"]
    
    def save(self):
        self.user.set_password(self.cleaned_data['password1'])
        self.user.save()
        self.user.message_set.create(message="Password successfully changed.")


class ResetPasswordForm(forms.Form):
    
    email = forms.EmailField(label="Email", required=True, widget=forms.TextInput(attrs={'size':'30'}))
    
    def clean_email(self):
        if EmailAddress.objects.filter(email__iexact=self.cleaned_data["email"], verified=True).count() == 0:
            raise forms.ValidationError(u"Email address not verified for any user account")
        return self.cleaned_data["email"]
    
    def save(self):
        for user in User.objects.filter(email__iexact=self.cleaned_data["email"]):
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            subject = "Password reset"
            message = render_to_string("account/password_reset_message.txt", {
                "user": user,
                "new_password": new_password,
            })
            # @@@ eventually use django-mailer
            if settings.DEBUG:
                print message
            else:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return self.cleaned_data["email"]