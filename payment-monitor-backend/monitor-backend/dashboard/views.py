from api.models import Payment
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.models import User
# Create your views here.


@login_required
def dashboard(request):
    payments = Payment.objects.filter(user=request.user)
    # print(payments.glm.count())
    glm_spent = 0.0
    matic_spent = 0.0
    for payment in payments:
        if payment.glm != None:
            glm_spent += payment.glm
            matic_spent += payment.matic
    print(matic_spent)
    return render(request, "dashboard.html", {'payments': payments, 'apikey': request.user.apikey, 'glm_spent': glm_spent, 'matic_spent': matic_spent})
