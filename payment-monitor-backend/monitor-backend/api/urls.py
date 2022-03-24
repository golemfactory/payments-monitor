from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'api'

urlpatterns = [
    path('payment', views.payment_endpoint),
    path('agreement', views.agreement_endpoint),
    path('provider', views.provider_endpoint),
    path('providernode', views.providernode_endpoint),
    path('invoice', views.invoice_endpoint),
]
