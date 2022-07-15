from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<str:region>/<str:realm>/', views.ProfessionIndexView.as_view()),
    path('<str:region>/<str:realm>/<str:profession>/', views.ProfessionTiersView.as_view(), name='profession-tiers'),
    path('<str:region>/<str:realm>/<str:profession>/<tier>/', views.RecipeCategoriesView.as_view(), name='recipe-categories'),
    path('<str:region>/<str:realm>/<str:profession>/<tier>/<int:pk>/', views.RecipeCalculatorView.as_view(), name='recipe-calculator'),
]
