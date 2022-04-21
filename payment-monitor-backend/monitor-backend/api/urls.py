from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'api'

urlpatterns = [
    path('payment/<apikey>', views.payment_endpoint),
    path('projects', views.projects.as_view()),
    path('agreement/<apikey>', views.agreement_endpoint),
    path('provider/<apikey>', views.provider_endpoint),
    path('providernode/<apikey>', views.providernode_endpoint),
    path('invoice/<apikey>', views.invoice_endpoint),
    path('agreement/to/invoice/<agreement_id>',
         views.agreement_to_invoice),
    path('agreement/to/activity/<agreement_id>',
         views.agreement_to_activity),
    path('activity/<apikey>', views.activity_endpoint),
]
