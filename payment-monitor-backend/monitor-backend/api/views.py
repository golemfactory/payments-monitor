from django.http import HttpResponse, JsonResponse
import json
import requests
from .models import Payment
from .tasks import check_tx_status
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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


@login_required
def dashboard(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, "dashboard.html", {'payments': payments})
