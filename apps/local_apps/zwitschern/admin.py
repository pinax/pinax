from django.contrib import admin
from zwitschern.models import Tweet, TweetInstance, Following

class TweetAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'text',)

class TweetInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'text', 'recipient_type', 'recipient_id')

class FollowingAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followed',)


admin.site.register(Tweet, TweetAdmin)
admin.site.register(TweetInstance, TweetInstanceAdmin)
admin.site.register(Following, FollowingAdmin)