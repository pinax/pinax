from datetime import datetime
from django import forms

from swaps.models import Offer, Swap

class OfferForm(forms.ModelForm):
    
    class Meta:
        model = Offer
        exclude = ('offerer', 'state', 'offered_time', 'swapped_by')
    

class ProposeSwapForm(forms.ModelForm):
    
    class Meta:
        model = Swap
        fields = ('proposing_offer',)
        
        
#    def __init__(self, user=None, *args, **kwargs):
#        if user:
#            self.fields['responding_offer'].queryset = Offer.objects.filter(offerer=user)
#        super(ProposeSwapForm, self).__init__(*args, **kwargs)




class ProposingOfferForm(forms.ModelForm):
    
    class Meta:
        model = Offer
        fields = ('short_description', 'offering',)
        