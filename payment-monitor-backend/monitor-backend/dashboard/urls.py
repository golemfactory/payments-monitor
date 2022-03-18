from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
]
