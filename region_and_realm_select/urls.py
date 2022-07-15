from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.RegionAndRealmFormRedirectView.as_view(), name='region-and-realm-form-redirect-view'),
    path('region-and-realm/', views.RegionAndRealmFormView.as_view(), name='region-and-realm-form-view'),
    path('', include('calculator.urls'), name='calculator')
]
