from django.contrib import admin
from swaps.models import Offer, Swap

class OfferAdmin(admin.ModelAdmin):
    list_display        = ('offerer', 'short_description', 'offering', 'want', 'state', 'swapped_by')
    list_filter         = ('offerer', 'state')
    search_fields       = ('short_description', 'offering', 'want')

admin.site.register(Offer, OfferAdmin)

class SwapAdmin(admin.ModelAdmin):
    list_display        = ('proposing_offer', 'responding_offer', 'state', 'conflicted_by')
    list_filter         = ('state',)

admin.site.register(Swap, SwapAdmin)