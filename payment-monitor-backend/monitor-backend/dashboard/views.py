from api.models import Payment
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.models import User
# Create your views here.


@login_required
def dashboard(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, "dashboard.html", {'payments': payments, 'apikey': request.user.apikey})
