from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'auth'

urlpatterns = [
    path('register', views.RegisterView.as_view()),
]
