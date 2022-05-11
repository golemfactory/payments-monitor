from api.models import Payment, Invoice, Activity
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.models import Project
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from api.serializers import PaymentSerializer, ActivitySerializer


class project_overview(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, apikey):
        project = Project.objects.get(apikey=apikey)
        payments = Payment.objects.filter(project=project)
        invoices = Invoice.objects.filter(
            project=project).aggregate(Sum('amount'))
        activites = Activity.objects.filter(
            project=project)
        spendings = {'spendings_glm': 0, 'spendings_matic': 0}
        payment_serializer = PaymentSerializer(payments, many=True)
        activity_serializer = ActivitySerializer(activites, many=True)
        for obj in payments:
            spendings['spendings_glm'] += obj.amount_human
            spendings['spendings_matic'] += obj.gas_spent_human
        return Response(status=200, data={"spendings": spendings, "provider_invoiced_amount": invoices, "payments": payment_serializer.data, "activities": activity_serializer.data})


class dashboard(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        project = Project.objects.filter(owner=request.user)
        activites = Activity.objects.filter(
            project=project)
        activity_serializer = ActivitySerializer(activites, many=True)
        return Response(status=200, data={"spendings": spendings, "provider_invoiced_amount": invoices, "payments": payment_serializer.data, "activities": activity_serializer.data})
