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
    # unique triple, these three values have to be unique on Ethereum based chain
    network = models.IntegerField(primary_key=True)
    nonce = models.BigIntegerField(primary_key=True)
    sender = models.CharField(primary_key=True, max_length=42, null=True, default=None)

    # reported specifically by yagna
    yagnaTimeCreated = models.DateTimeField()
    yagnaTimeLastAction = models.DateTimeField()
    yagnaTimeSent = models.DateTimeField()
    yagnaTimeConfirmed = models.DateTimeField()
    yagnaStartingGasPrice = models.CharField(
        max_length=128, null=True, default=None)
    yagnaMaximumGasPrice = models.CharField(
        max_length=128, null=True, default=None)
    yagnaStatus = models.IntegerField()

    # final transaction hash if payment successful
    finalTx = models.CharField(max_length=70, unique=True)

    # public data reported by yagna, but also possible to be confirmed on chain
    recipient = models.CharField(max_length=42, null=True, default=None)
    gasUsed = models.IntegerField()
    gasLimit = models.IntegerField()
    gasPrice = models.CharField(max_length=128, null=True, default=None)

    # not needed for convenience only
    amountHuman = models.FloatField(null=True, default=None)
    gasSpentHuman = models.FloatField(null=True, default=None)
    gasPriceGwei = models.FloatField(null=True, default=None)

    # internal
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['network', 'nonce', 'sender'], name='primary_transaction_triple')
        ]


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
