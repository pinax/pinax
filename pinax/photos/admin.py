from django.contrib import admin
from photos.models import Photos, Pool

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_slug', 'caption','date_added','is_public','member','safetylevel','tags',)    

class PoolAdmin(admin.ModelAdmin):
    list_display = ('photo', )

admin.site.register(Photos, PhotoAdmin)
admin.site.register(Pool, PoolAdmin)
