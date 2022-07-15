from django import forms
from calculator.models import Realm
#2 options
#make one form that uses the selected region to query the db for its realms and provide those as choices
#make two pages one for region and another that uses the session['region'] to provide a form of realms

#problem with one is that I know it can be done with js by making a request to the db when the region is selected
#but i don't know how to do that with django as i skipped learning forms

#problem with the second one is having to make two pages. This one saounds nice
class RegionAndRealmForm(forms.Form):

    region_choices = (
        ('North America', 'Americas and Oceania'),
        ('Europe', 'Europe'),
        ('Korea', 'Korea'),
    )

    region = forms.ChoiceField(choices=region_choices)
    na_realm = forms.ModelChoiceField(queryset=Realm.objects.filter(region='North America'), label="North American Realms")
    eu_realm = forms.ModelChoiceField(queryset=Realm.objects.filter(region='Europe'), label="European Realms")
    kr_realm = forms.ModelChoiceField(queryset=Realm.objects.filter(region='Korea'), label="Korean Realms")