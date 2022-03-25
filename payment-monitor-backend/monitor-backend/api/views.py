from django.http import HttpResponse, JsonResponse
import json
import requests
from api.models.models import Payment, Invoice, Agreement, ProviderNode, Project, Provider, RequestorNode, Activity
from .tasks import check_tx_status
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async


@sync_to_async
@csrf_exempt
@async_to_sync
async def process_payment(request):
    """
    Endpoint to receive payment info and send it to the celery workers for checking.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        check_tx_status.delay(
            data['tx'], data['key'])
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def agreement_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        providerObj, providerObjCreated = Provider.objects.get_or_create(
            walletAddress=data['provider']['wallet_address'], project=project)
        if "name" in data['provider']:
            providerObj.name = data['provider']['name']
            providerObj.save()
        else:
            providerObj.save()
        providerNodeObj, providerNodeObjcreated = ProviderNode.objects.get_or_create(
            provider_id=data['provider']['provider_id'], subnet=data['provider']['subnet'], project=project, linked_provider=providerObj)
        Agreement.objects.get_or_create(
            agreement_id=data['agreement_id'], project=project, providernode=providerNodeObj)
        return HttpResponse(status=201)
    elif request.method == 'GET':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        agreement = Agreement.objects.get(agreement_id=data['agreement_id'])
        if agreement.project == project:
            return JsonResponse(agreement, json_dumps_params={'indent': 4})
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def invoice_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        agreement = Agreement.objects.get(agreement_id=data['agreement_id'])
        if "payment" in data:
            payment = Payment.objects.create(project=project, tx=data['payment']['tx_id'], status=data['payment']['status'], sender=data['payment']['sender'], recipient=data['payment']['recipient'],  glm=data[
                                             'payment']['glm'], matic=data['payment']['matic'], gasUsed=data['payment']['gas_used'], gasPrice=data['payment']['gas_price'], gasPriceGwei=data['payment']['gas_price_gwei'])
            invoice = Invoice.objects.create(amount=data['amount'], invoice_id=data['invoice_id'],
                                             issuer_id=data['issuer_id'], payment_platform=data['payment_platform'], agreement=agreement, project=project, linked_payment=payment)
            payment.linked_invoice = invoice
            payment.save()
        else:
            Invoice.objects.create(amount=data['amount'], invoice_id=data['invoice_id'],
                                   issuer_id=data['issuer_id'], payment_platform=data['payment_platform'], agreement=agreement, project=project)
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
        payment = Payment.objects.get(tx=data['tx_id'])
        payment.linked_invoice = invoice
        payment.save()
        invoice.linked_payment = payment
        invoice.save()
        return HttpResponse(status=200)


@csrf_exempt
def payment_endpoint(request):
    if 0:
        if request.method == 'POST':
            data = json.loads(request.body)
            project = Project.objects.get(apikey=data['apikey'])
            payment = Payment.objects.create(project=project, tx=data['tx_id'], status=data['status'], sender=data['sender'], recipient=data['recipient'],
                                             glm=data['glm'], matic=data['matic'], gasUsed=data['gas_used'], gasPrice=data['gas_price'], gasPriceGwei=['gas_price_gwei'])
            if "invoice_id" in data:
                invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
                payment = Payment.objects.create(project=project, tx=data['tx_id'], status=data['status'], sender=data['sender'], recipient=data['recipient'],
                                                 glm=data['glm'], matic=data['matic'], gasUsed=data['gas_used'], gasPrice=data['gas_price'], gasPriceGwei=['gas_price_gwei'], linked_invoice=invoice)
                invoice.linked_payment = payment
                invoice.save()
            return HttpResponse(status=201)
        elif request.method == 'PATCH':
            data = json.loads(request.body)
            project = Project.objects.get(apikey=data['apikey'])
            payment = Payment.objects.get(tx=data['tx'])
            invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
            payment.linked_invoice = invoice
            payment.save()
            invoice.linked_payment = payment
            invoice.save()
            return HttpResponse(status=200)


@csrf_exempt
def provider_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        provider = Provider.objects.create(
            walletAddress=data['wallet_address'], project=project)
        if "name" in data:
            provider.name = data['name']
            provider.save()
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        provider = Provider.objects.get(walletAddress=data['wallet_address'])
        provider.name = data['name']
        provider.save()


@csrf_exempt
def providernode_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        providerObj, providerObjCreated = Provider.objects.get_or_create(
            walletAddress=data['wallet_address'], project=project)
        if "name" in data:
            providerObj.name = data['name']
            providerObj.save()
        else:
            providerObj.save()
        providerNodeObj = ProviderNode.objects.get_or_create(
            provider_id=data['provider_id'], subnet=data['subnet'], project=project, linked_provider=providerObj)
        return HttpResponse(status=201)
