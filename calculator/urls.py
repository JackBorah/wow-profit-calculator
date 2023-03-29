from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<str:region>/<str:realm>/', views.ProfessionIndexView.as_view(), name='select-profession'), #works
    path('<region>/<realm>/<profession>/', views.ProfessionTiersIndexView.as_view(), name='select-profession-tier'), #works
    path('<region>/<realm>/<profession>/<tier>/', views.ProfessionTierCategoriesIndexView.as_view(), name='select-recipe-category'),
    path('<str:region>/<str:realm>/<str:profession>/<tier>/<int:pk>/', views.RecipeCalculatorView.as_view(), name='select-recipe'),
]
