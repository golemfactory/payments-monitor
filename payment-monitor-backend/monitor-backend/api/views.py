from django.http import HttpResponse, JsonResponse
import json
import requests
from .models import Payment
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
        received_json_data = json.loads(request.body)
        check_tx_status.delay(
            received_json_data['tx'], received_json_data['key'])
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)
