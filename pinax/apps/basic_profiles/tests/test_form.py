# coding: utf-8

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from basic_profiles.forms import ProfileForm
from basic_profiles.models import Profile



class TestProfileForm(TestCase):
    fixtures = ['test_basic_profiles.json']
    
    def setUp(self):
        self.user = User.objects.get(username='bob')
        self.profile = Profile.objects.get(user=self.user)
    
    def tearDown(self):
        pass
        
    def test_profile_form(self):
        form = ProfileForm(instance=self.profile)
        # include a bad url to force an error
        data = {
            "name": "John Smith",
            "about": "John likes wine",
            "location": "France maybe!",
            "website": "httpasd://python.org"
        }
        form = ProfileForm(data)
        self.assertEquals(False, form.is_valid())
