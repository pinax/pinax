from django.contrib import admin
from photos.models import Image, Pool

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_slug', 'caption','date_added','is_public','member','safetylevel','tags',)    

class PoolAdmin(admin.ModelAdmin):
    list_display = ('photo', )

admin.site.register(Image, PhotoAdmin)
admin.site.register(Pool, PoolAdmin)
