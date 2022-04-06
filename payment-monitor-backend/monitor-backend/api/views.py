import base64
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
async def process_payment(request, apikey):
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
def agreement_endpoint(request, apikey):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)

        providerObj, providerObjCreated = Provider.objects.update_or_create(
            wallet_address=data['provider']['wallet_address'],
            project=project
        )
        if "name" in data['provider']:
            providerObj.name = data['provider']['name']
            providerObj.save()
        else:
            providerObj.save()

        providerNodeObj, providerNodeObjcreated = ProviderNode.objects.update_or_create(
            node_id=data['provider']['provider_id'],
            subnet=data['provider']['subnet'],
            project=project,
            linked_provider=providerObj
        )

        Agreement.objects.update_or_create(
            agreement_id=data['agreement_id'],
            project=project,
            provider_node=providerNodeObj,
            defaults={
                'amount_due': data['amount_due'],
                'amount_accepted': data['amount_accepted'],
                'amount_scheduled': data['amount_scheduled'],
                'amount_paid': data['amount_paid'],
                'state': data['state'],
                'demand_properties': json.loads(base64.b64decode(data["demand_properties"].encode('ascii')).decode("utf-8")),
                'demand_constraints': base64.b64decode(data["demand_constraints"].encode('ascii')).decode("utf-8"),
                'offer_properties': json.loads(base64.b64decode(data["offer_properties"].encode('ascii')).decode("utf-8")),
                'offer_constraints': base64.b64decode(data["offer_constraints"].encode('ascii')).decode("utf-8"),

                'creation_ts': data["creation_ts"],
                'approved_ts': data["approved_ts"],
                'valid_to': data["valid_to"]
            }
        )

        return HttpResponse(status=201)
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        agreement = Agreement.objects.filter(project=project).values()
        if agreement:
            return JsonResponse(list(agreement), json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


def get_payment_id(sender, network, nonce):
    payload = sender + "_" + str(network) + "_" + str(nonce)
    payment_id = hashlib.sha1(payload.encode('utf-8')).hexdigest()
    return payment_id


@csrf_exempt
def invoice_endpoint(request, apikey):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        agreement = Agreement.objects.get(agreement_id=data['agreement_id'])
        payment = None
        if "payment" in data and data["payment"]:
            sender = data['payment']['sender'].lower()
            recipient = data['payment']['recipient'].lower()

            payment_id = get_payment_id(
                sender, data['payment']['network'], data['payment']['nonce'])

            payment, _ = Payment.objects.update_or_create(
                id=payment_id,
                project=project,
                defaults={
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
            project=project,
            defaults={
                'amount': data['amount'],
                'issuer_id': data['issuer_id'],
                'invoice_status': data['invoice_status'],
                'payment_platform': data['payment_platform'],
                'is_debit_note': data['is_debit_note'],
                'agreement': agreement,
                'linked_payment': payment,
            })

        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
        payment = Payment.objects.get(tx=data['tx_id'])
        payment.linked_invoice = invoice
        payment.save()
        invoice.linked_payment = payment
        invoice.save()
        return HttpResponse(status=200)
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        invoices = Invoice.objects.filter(project=project).values()
        if invoices:
            return JsonResponse(list(invoices), json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def payment_endpoint(request, apikey):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
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
        project = Project.objects.get(apikey=apikey)
        payment = Payment.objects.get(tx=data['tx'])
        invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
        payment.save()
        invoice.linked_payment = payment
        invoice.save()
        return HttpResponse(status=200)
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        payments = Payment.objects.filter(project=project).values()
        if payments:
            return JsonResponse(list(payments), json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def provider_endpoint(request, apikey):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        provider = Provider.objects.create(
            wallet_address=data['wallet_address'], project=project)
        if "name" in data:
            provider.name = data['name']
            provider.save()
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        provider = Provider.objects.get(wallet_address=data['wallet_address'])
        provider.name = data['name']
        provider.save()
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        providers = Provider.objects.filter(project=project).values()
        if providers:
            return JsonResponse(list(providers), json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def activity_endpoint(request, apikey):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        requestor_agent, _ = RequestorAgent.objects.update_or_create(
            requestor_id=data['requestor']['requestor_id'],
            project=project,
            defaults={
                'wallet_address': data['requestor']['wallet_address'],
                'node_name': data['requestor']['node_name']
            }
        )

        provider_node_obj = ProviderNode.objects.get(
            node_id=data['provider']['provider_id'],
            project=project
        )

        agreement_obj = Agreement.objects.get(agreement_id=data['agreement_id'])

        activity, created = Activity.objects.update_or_create(
            activity_id=data['activity_id'],
            project=project,
            defaults={
                'task_status': data['task_status'],
                'job_cost': data['job_cost'],
                'cpu_time': data['cpu_time'],
                'job_unit': data['job_unit'],
                'job_quantity': data['job_quantity'],
                'job_name': data['job_name'],
                'provider_node': provider_node_obj,
                'requestor_node': requestor_agent,
                'agreement': agreement_obj,
                'amount_due': data['amount_due'],
                'amount_accepted': data['amount_accepted'],
                'amount_scheduled': data['amount_scheduled'],
                'amount_paid': data['amount_paid'],
                'usage_cost': data['usage_cost']
            }
        )

        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        if 0:
            data = json.loads(request.body)
            project = Project.objects.get(apikey=apikey)
            activity = Activity.objects.get(
                unique_identifier=data['unique_identifier'])
            invoice = Activity.objects.get(invoice_id=data['invoice_id'])
            activity.invoice = invoice
            activity.save()
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        activites = Activity.objects.filter(project=project).values()
        if activites:
            return JsonResponse(list(activites), json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def providernode_endpoint(request, apikey):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        providerObj, providerObjCreated = Provider.objects.update_or_create(
            wallet_address=data['wallet_address'], project=project)

        providerNodeObj = ProviderNode.objects.update_or_create(
            node_id=data['provider_id'], node_name=data['name'], subnet=data['subnet'], project=project,
            linked_provider=providerObj)
        return HttpResponse(status=201)
    elif request.method == 'GET':
        project = Project.objects.get(apikey=apikey)
        providernodes = ProviderNode.objects.filter(project=project).values()
        if providernodes:
            return JsonResponse(list(providernodes), json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)
