from django import forms
from calculator.models import Realm

class RegionAndRealmForm(forms.Form):

    region_choices = (
        ('North America', 'Americas and Oceania'),
        ('Europe', 'Europe'),
        ('Korea', 'Korea'),
    )

    region = forms.ChoiceField(choices=region_choices)
    na_realm = forms.ModelChoiceField(queryset=Realm.objects.filter(region='us'), label="North American Realms")
    # eu_realm = forms.ModelChoiceField(queryset=Realm.objects.filter(region='eu'), label="European Realms")
    # kr_realm = forms.ModelChoiceField(queryset=Realm.objects.filter(region='kr'), label="Korean Realms")