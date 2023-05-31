from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from . import forms
from calculator.models import Realm


# Create your views here.

class RegionAndRealmFormRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.session.get('region') and self.request.session.get('realm'):
            region = self.request.session.get('region')
            realm = self.request.session.get('realm')
            self.url = f'{region}/{realm}/'
        else:
            self.pattern_name = 'region-and-realm-form-view' 
        return super().get_redirect_url(*args, **kwargs)


class RegionAndRealmFormView(FormView):
    template_name = 'region_and_realm_form.html'
    form_class = forms.RegionAndRealmForm
    success_url = '/'

    def form_valid(self, form):
        self.request.session['region'] = form.cleaned_data['region']
        self.request.session['realm'] = form.cleaned_data['na_realm'].name
        return super().form_valid(form)
