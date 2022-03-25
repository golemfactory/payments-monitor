from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    apikey = models.UUIDField(default=uuid.uuid4, editable=True)


class Project(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    apikey = models.UUIDField(default=uuid.uuid4, editable=True)


class RequestorNode(models.Model):
    walletAddress = models.CharField(max_length=42)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Provider(models.Model):
    walletAddress = models.CharField(max_length=42)
    name = models.CharField(max_length=128, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class ProviderNode(models.Model):
    provider_id = models.CharField(max_length=42)
    linked_provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    subnet = models.CharField(max_length=128)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Agreement(models.Model):
    agreement_id = models.CharField(max_length=128)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    providernode = models.ForeignKey(ProviderNode, on_delete=models.CASCADE)


class Payment(models.Model):
    tx = models.CharField(max_length=70, unique=True)
    status = models.CharField(max_length=35)
    sender = models.CharField(max_length=42, null=True, default=None)
    recipient = models.CharField(max_length=42, null=True, default=None)
    glm = models.FloatField(null=True, default=None)
    matic = models.FloatField(null=True, default=None)
    gasUsed = models.BigIntegerField(null=True, default=None)
    gasPrice = models.BigIntegerField(null=True, default=None)
    gasPriceGwei = models.FloatField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Invoice(models.Model):
    amount = models.CharField(max_length=128)
    invoice_id = models.UUIDField()
    issuer_id = models.CharField(max_length=42)
    payment_platform = models.CharField(max_length=64)
    agreement = models.ForeignKey('api.Agreement', on_delete=models.CASCADE)
    project = models.ForeignKey('api.Project', on_delete=models.CASCADE)
    linked_payment = models.ForeignKey(
        'api.Payment', on_delete=models.CASCADE, null=True, blank=True)



class Activity(models.Model):
    providerNode = models.ForeignKey(ProviderNode, on_delete=models.CASCADE)
    requestorNode = models.ForeignKey(RequestorNode, on_delete=models.CASCADE)
    jobName = models.CharField(max_length=64)
    jobQuantity = models.FloatField()
    jobUnit = models.CharField(max_length=64)
    cpuTime = models.FloatField()
    jobCost = models.FloatField()
    payment = models.ForeignKey(
        Payment, null=True, blank=True, on_delete=models.CASCADE)
    agreement = models.ForeignKey(
        Agreement, null=True, blank=True, on_delete=models.CASCADE)
    taskStatus = models.CharField(max_length=64)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
