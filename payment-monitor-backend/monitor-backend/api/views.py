from operator import inv
from django.http import HttpResponse, JsonResponse
import json
import requests
from api.models import Payment, Invoice, Agreement, ProviderNode, Project, Provider, RequestorAgent, Activity
from .tasks import check_tx_status
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
import hashlib


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
def agreement_endpoint(request, apikey=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        providerObj, providerObjCreated = Provider.objects.get_or_create(
            wallet_address=data['provider']['wallet_address'], project=project)
        if "name" in data['provider']:
            providerObj.name = data['provider']['name']
            providerObj.save()
        else:
            providerObj.save()
        providerNodeObj, providerNodeObjcreated = ProviderNode.objects.get_or_create(
            node_id=data['provider']['provider_id'], subnet=data['provider']['subnet'], project=project,
            linked_provider=providerObj)
        Agreement.objects.get_or_create(
            agreement_id=data['agreement_id'], project=project, provider_node=providerNodeObj)
        return HttpResponse(status=201)
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        agreement = Agreement.objects.filter(project=project)
        if agreement:
            return JsonResponse(agreement, json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


def get_payment_id(sender, network, nonce):
    payload = sender + "_" + str(network) + "_" + str(nonce)
    payment_id = hashlib.sha1(payload.encode('utf-8')).hexdigest()
    return payment_id


@csrf_exempt
def invoice_endpoint(request, apikey=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        agreement = Agreement.objects.get(agreement_id=data['agreement_id'])
        payment = None
        if "payment" in data and data["payment"]:
            sender = data['payment']['sender'].lower()
            recipient = data['payment']['recipient'].lower()

            payment_id = get_payment_id(
                sender, data['payment']['network'], data['payment']['nonce'])

            payment, _ = Payment.objects.update_or_create(
                id=payment_id,
                defaults={
                    'project': project,
                    'network': data['payment']['network'],
                    'nonce': data['payment']['nonce'],
                    'sender': sender,

                    'yagna_time_created': data['payment']['time_created'],
                    'yagna_time_last_action': data['payment']['time_last_action'],
                    'yagna_time_sent': data['payment']['time_sent'],
                    'yagna_time_confirmed': data['payment']['time_confirmed'],
                    'yagna_starting_gas_price': data['payment']['starting_gas_price'],
                    'yagna_maximum_gas_price': data['payment']['max_gas_price'],
                    'yagna_status': data['payment']['status'],

                    'final_tx': data['payment']['tx_id'],

                    'recipient': recipient,
                    'gas_used': data['payment']['final_gas_used'],
                    'gas_limit': data['payment']['gas_limit'],
                    'gas_price': data['payment']['current_gas_price'],

                    'amount_human': data['payment']['amount_human'],
                    'gas_spent_human': data['payment']['gas_spent_human'],
                    'gas_price_gwei': data['payment']['gas_price_gwei']
                })

        invoice, _ = Invoice.objects.update_or_create(
            invoice_id=data['invoice_id'],
            defaults={
                'amount': data['amount'],
                'issuer_id': data['issuer_id'],
                'invoice_status': data['invoice_status'],
                'payment_platform': data['payment_platform'],
                'is_debit_note': data['is_debit_note'],
                'agreement': agreement,
                'project': project,
                'linked_payment': payment,
            })

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
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        invoices = Invoice.objects.filter(project=project)
        if invoices:
            return JsonResponse(invoices, json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def payment_endpoint(request, apikey=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        payment = Payment.objects.create(project=project, tx=data['tx_id'], status=data['status'],
                                         sender=data['sender'], recipient=data['recipient'],
                                         glm=data['glm'], matic=data['matic'], gasUsed=data['gas_used'],
                                         gasPrice=data['gas_price'], gasPriceGwei=['gas_price_gwei'])
        if "invoice_id" in data:
            invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
            payment = Payment.objects.create(project=project, tx=data['tx_id'], status=data['status'],
                                             sender=data['sender'], recipient=data['recipient'],
                                             glm=data['glm'], matic=data['matic'], gasUsed=data['gas_used'],
                                             gasPrice=data['gas_price'], gasPriceGwei=[
                'gas_price_gwei'],
                linked_invoice=invoice)
            invoice.linked_payment = payment
            invoice.save()
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        payment = Payment.objects.get(tx=data['tx'])
        invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
        payment.save()
        invoice.linked_payment = payment
        invoice.save()
        return HttpResponse(status=200)
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        payments = Payment.objects.filter(project=project)
        if payments:
            return JsonResponse(payments, json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def provider_endpoint(request, apikey=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        provider = Provider.objects.create(
            wallet_address=data['wallet_address'], project=project)
        if "name" in data:
            provider.name = data['name']
            provider.save()
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        provider = Provider.objects.get(wallet_address=data['wallet_address'])
        provider.name = data['name']
        provider.save()
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        providers = Provider.objects.filter(project=project)
        if providers:
            return JsonResponse(providers, json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def activity_endpoint(request, apikey=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        requestorAgent, _ = RequestorAgent.objects.get_or_create(
            requestor_id=data['requestor']['requestor_id'],
            wallet_address=data['requestor']['wallet_address'],
            node_name=data['requestor']['node_name'],
            project=project)

        providerNodeObj = ProviderNode.objects.get(
            node_id=data['provider']['provider_id'],
            project=project
        )

        invoice = None
        if "invoice_id" in data:
            invoice = Invoice.objects.get(invoice_id=data['invoice_id'])

        agreementObj = Agreement.objects.get(agreement_id=data['agreement_id'])

        activity = Activity.objects.create(project=project, task_status=data['task_status'], job_cost=data['job_cost'],
                                           cpu_time=data['cpu_time'], job_unit=data['job_unit'],
                                           job_quantity=data['job_quantity'], job_name=data['job_name'],
                                           provider_node=providerNodeObj, requestor_node=requestorAgent,
                                           agreement=agreementObj, activity_id=data['activity_id'],
                                           invoice=invoice)

        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        if 0:
            data = json.loads(request.body)
            project = Project.objects.get(apikey=data['apikey'])
            activity = Activity.objects.get(
                unique_identifier=data['unique_identifier'])
            invoice = Activity.objects.get(invoice_id=data['invoice_id'])
            activity.invoice = invoice
            activity.save()
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        activites = Activity.objects.filter(project=project)
        if activites:
            return JsonResponse(activites, json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def providernode_endpoint(request, apikey=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=data['apikey'])
        providerObj, providerObjCreated = Provider.objects.get_or_create(
            wallet_address=data['wallet_address'], project=project)

        providerNodeObj = ProviderNode.objects.get_or_create(
            node_id=data['provider_id'], node_name=data['name'], subnet=data['subnet'], project=project,
            linked_provider=providerObj)
        return HttpResponse(status=201)
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        providernodes = ProviderNode.objects.filter(project=project)
        if providernodes:
            return JsonResponse(providernodes, json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)
