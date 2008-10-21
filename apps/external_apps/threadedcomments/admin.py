from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from threadedcomments.models import ThreadedComment, FreeThreadedComment

class ThreadedCommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('content_type', 'object_id')}),
        (_('Parent'), {'fields' : ('parent',)}),
        (_('Content'), {'fields': ('user', 'comment')}),
        (_('Meta'), {'fields': ('is_public', 'date_submitted', 'date_modified', 'date_approved', 'is_approved', 'ip_address')}),
    )
    list_display = ('user', 'date_submitted', 'content_type', 'get_content_object', 'parent', '__unicode__')
    list_filter = ('date_submitted',)
    date_hierarchy = 'date_submitted'
    search_fields = ('comment', 'user__username')

class FreeThreadedCommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('content_type', 'object_id')}),
        (_('Parent'), {'fields' : ('parent',)}),
        (_('Content'), {'fields': ('name', 'website', 'email', 'comment')}),
        (_('Meta'), {'fields': ('date_submitted', 'date_modified', 'date_approved', 'is_public', 'ip_address', 'is_approved')}),
    )
    list_display = ('name', 'date_submitted', 'content_type', 'get_content_object', 'parent', '__unicode__')
    list_filter = ('date_submitted',)
    date_hierarchy = 'date_submitted'
    search_fields = ('comment', 'name', 'email', 'website')


admin.site.register(ThreadedComment, ThreadedCommentAdmin)
admin.site.register(FreeThreadedComment, FreeThreadedCommentAdmin)
