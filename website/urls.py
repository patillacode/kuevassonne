from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.index, name='create'),
    path('games/', views.index, name='games'),
    path('records/', views.index, name='records'),
]
