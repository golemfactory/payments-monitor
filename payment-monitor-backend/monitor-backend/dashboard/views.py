from api.models import Payment
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.models import Project
# Create your views here.


@login_required
def dashboard(request):
    # payments = Payment.objects.filter(user=request.user)
    project = Project.objects.create(name="test1", owner=request.user)
    # print(payments.glm.count())
    glm_spent = 0.0
    matic_spent = 0.0
    # for payment in payments:
    #     if payment.glm != None:
    #         glm_spent += payment.glm
    #         matic_spent += payment.matic
    print(matic_spent)
    return render(request, "dashboard.html", {'apikey': request.user.apikey,  "project": project.apikey})
