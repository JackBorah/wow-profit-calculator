from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<str:region>/<str:realm>/', views.ProfessionIndexView.as_view(), name='select-profession'), #works
    # path('<region>/<realm>/<profession>/', views.ProfessionTiersIndexView.as_view(), name='select-profession-tier'), #works
    path('<region>/<realm>/<profession>/', views.ProfessionCategoriesView.as_view(), name='select-recipe-category'),
    path('<str:region>/<str:realm>/<str:profession>/<category>/<int:pk>/', views.RecipeCalculatorView.as_view(), name='recipe-calculator'),
]
