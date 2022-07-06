import base64
from django.http import HttpResponse, JsonResponse
import json

from api.models import Payment, Invoice, Agreement, ProviderNode, Project, Provider, RequestorAgent, Activity
from django.views.decorators.csrf import csrf_exempt
import hashlib
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .utils import save_log


class agreement_endpoint(APIView):
    def get(self, request, apikey):
        project = Project.objects.get(apikey=apikey)
        agreement = Agreement.objects.filter(project=project).values()
        if agreement:
            return JsonResponse(list(agreement), json_dumps_params={'indent': 4}, safe=False)
        else:
            return HttpResponse(status=404)

    def post(self, request, apikey):
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)

        providerObj, providerObjCreated = Provider.objects.update_or_create(
            wallet_address=data['provider']['wallet_address'],
            project=project
        )
        if "name" in data['provider']:
            providerObj.name = data['provider']['name']
            providerObj.save()
            save_log(
                project, f"Linked provider {data['provider']['name']} to wallet {data['provider']['wallet_address'][0:5]}")
        else:
            providerObj.save()
            save_log(
                project, f"Created provider {data['provider']['name']} linked to wallet {data['provider']['wallet_address'][0:5]}")

        providerNodeObj, providerNodeObjcreated = ProviderNode.objects.update_or_create(
            node_id=data['provider']['provider_id'],
            subnet=data['provider']['subnet'],
            project=project,
            linked_provider=providerObj
        )
        if providerNodeObjcreated:
            save_log(
                project, f"Created provider node with id {data['provider']['provider_id'][0:5]} and subnet {data['provider']['subnet']}")
        else:
            save_log(
                project, f"Updated provider node with id {data['provider']['provider_id'][0:5]} and subnet {data['provider']['subnet']}")

        obj, created = Agreement.objects.update_or_create(
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
        if created:
            save_log(
                project, f"Created agreement with id {data['agreement_id'][0:5]}")
        else:
            save_log(
                project, f"Updated agreement with id {data['agreement_id'][0:5]}")

        return HttpResponse(status=201)


@csrf_exempt
def agreement_to_invoice(request, agreement_id):
    if request.method == 'GET':
        agreement = Agreement.objects.get(agreement_id=agreement_id)
        invoice = Invoice.objects.filter(agreement=agreement).values()
        return JsonResponse(list(invoice), json_dumps_params={'indent': 4}, safe=False)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def agreement_to_activity(request, agreement_id):
    if request.method == 'GET':
        agreement = Agreement.objects.get(agreement_id=agreement_id)
        activity = Activity.objects.filter(agreement=agreement).values()
        data = []
        for obj in activity:
            provider = ProviderNode.objects.get(id=obj['provider_node_id'])
            obj.update({'provider': {
                'provider_node': provider.node_id,
                'node_name': provider.node_name,
                'subnet': provider.subnet
            }})
            data.append(obj)
        return JsonResponse(data, json_dumps_params={'indent': 4}, safe=False)
    else:
        return HttpResponse(status=400)


def get_payment_id(sender, network, nonce):
    payload = sender + "_" + str(network) + "_" + str(nonce)
    payment_id = hashlib.sha1(payload.encode('utf-8')).hexdigest()
    return payment_id


@ csrf_exempt
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

            payment, paymentcreated = Payment.objects.update_or_create(
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
            if paymentcreated:
                save_log(
                    project, f"Created payment with id {payment_id[0:5]} ")
            else:
                save_log(
                    project, f"Updated payment with id {payment_id[0:5]} ")

        invoice, invoicecreated = Invoice.objects.update_or_create(
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
        if invoicecreated:
            save_log(
                project, f"Created invoice with id {data['invoice_id'][0:5]} ")
        else:
            save_log(
                project, f"Updated invoice with id {data['invoice_id'][0:5]} ")

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
        save_log(
            project, f"Linked invoice with id {data['invoice_id'][0:5]} to {payment.id[0:5]} ")
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


@ csrf_exempt
def payment_endpoint(request, apikey):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        payment = Payment.objects.create(project=project, tx=data['tx_id'], status=data['status'],
                                         sender=data['sender'], recipient=data['recipient'],
                                         glm=data['glm'], matic=data['matic'], gasUsed=data['gas_used'],
                                         gasPrice=data['gas_price'], gasPriceGwei=['gas_price_gwei'])
        save_log(
            project, f"Created payment object linked to transaction id {data['tx_id'][0:5]} ")
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
            save_log(
                project, f"Linked transaction with id {data['tx_id'][0:5]} to {invoice.id[0:5]} ")
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        payment = Payment.objects.get(tx=data['tx'])
        invoice = Invoice.objects.get(invoice_id=data['invoice_id'])
        payment.save()
        invoice.linked_payment = payment
        invoice.save()
        save_log(
            project, f"Linked transaction with id {data['tx'][0:5]} to invoice {invoice.id[0:5]} ")
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
            save_log(
                project, f"Created provider with name {data['name']} linked to wallet address {data['wallet_address'][0:5]} ")
        else:
            save_log(
                project, f"Created provider with address {data['wallet_address'][0:5]} ")
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        project = Project.objects.get(apikey=apikey)
        provider = Provider.objects.get(wallet_address=data['wallet_address'])
        provider.name = data['name']
        provider.save()
        save_log(
            project, f"Updated name for provider with address {data['wallet_address'][0:5]} to {data['name']} ")
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
        requestor_agent, requestor_agent_created = RequestorAgent.objects.update_or_create(
            requestor_id=data['requestor']['requestor_id'],
            project=project,
            defaults={
                'wallet_address': data['requestor']['wallet_address'],
                'node_name': data['requestor']['node_name']
            }
        )
        if requestor_agent_created:
            save_log(
                project, f"Created requestor agent with id {data['requestor']['requestor_id'][0:5]} ")
        else:
            save_log(
                project, f"Updated requestor agent with id {data['requestor']['requestor_id'][0:5]} ")

        provider_node_obj = ProviderNode.objects.get(
            node_id=data['provider']['provider_id'],
            project=project
        )

        agreement_obj = Agreement.objects.get(
            agreement_id=data['agreement_id'])

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
        if created:
            save_log(
                project, f"Created activity with id {data['activity_id'][0:5]} for job {data['job_name']} ")
        else:
            save_log(
                project, f"Updated activity with id {data['activity_id'][0:5]} for job {data['job_name']} ")
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
            save_log(
                project, f"Linked invoice with id {data['invoice_id'][0:5]} to activity {activity.id[0:5]} ")
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

        providerNodeObj, providerNodeObjCreated = ProviderNode.objects.update_or_create(
            node_id=data['provider_id'], node_name=data['name'], subnet=data['subnet'], project=project,
            linked_provider=providerObj)
        if providerNodeObjCreated:
            save_log(
                project, f"Created provider node with id {data['provider_id'][0:5]} and name {data['name']} on subnet {data['subnet']} ")
        else:
            save_log(
                project, f"Updated provider node with id {data['provider_id'][0:5]} and name {data['name']} on subnet {data['subnet']} ")
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


# @api_view(['GET'])
# @csrf_exempt
# @permission_classes([IsAuthenticated])
# def projects(request):
#     if request.method == 'GET':
#         projects = Project.objects.filter(owner=request.user).values()
#         return JsonResponse(list(projects), json_dumps_params={'indent': 4}, safe=False)
#     # elif request.method == 'POST':
#     #     data = json.loads(request.body)
#     #     project = Project.objects.create(name=data['name'], owner=request.user)
#     #     return JsonResponse(list(project), json_dumps_params={'indent': 4}, safe=False)
#     # else:
#     #     return HttpResponse(status=400)


class projects(APIView):
    permission_classes = (IsAuthenticated,)             # <-- And here

    def get(self, request):
        projects = Project.objects.filter(owner=request.user).values()
        return JsonResponse(list(projects), json_dumps_params={'indent': 4}, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        project = Project.objects.create(name=data['name'], owner=request.user)
        return Response(status=201, data={'status': 'created', 'id': project.id, 'name': project.name, 'owner': project.owner.username, 'apikey': project.apikey})
