from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'dashboard'

urlpatterns = [
    path('project/<apikey>', views.project_overview.as_view(),
         name="project_overview"),
]
