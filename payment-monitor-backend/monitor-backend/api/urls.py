from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'api'

urlpatterns = [
    path('payment', views.process_payment),
    path('dashboard', views.dashboard, name="dashboard"),
]
