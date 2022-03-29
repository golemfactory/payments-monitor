from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    apikey = models.UUIDField(default=uuid.uuid4, editable=True)


class Project(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    apikey = models.UUIDField(default=uuid.uuid4, editable=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)


# Basically requestor node
class RequestorAgent(models.Model):
    requestor_id = models.CharField(max_length=40, primary_key=True)
    wallet_address = models.CharField(max_length=42)
    node_name = models.CharField(max_length=128, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Provider(models.Model):
    id = models.UUIDField(primary_key=True)
    # wallet_address - this pair should be unique (wallet_address, project)
    wallet_address = models.CharField(max_length=42)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class ProviderNode(models.Model):
    id = models.UUIDField(primary_key=True)
    # system node id - this pair should be unique (node_id, project)
    node_id = models.CharField(max_length=40)
    linked_provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    node_name = models.CharField(max_length=128, null=True, blank=True)
    subnet = models.CharField(max_length=128)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Agreement(models.Model):
    agreement_id = models.CharField(max_length=128, primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    provider_node = models.ForeignKey(ProviderNode, on_delete=models.CASCADE)


class Payment(models.Model):
    # unique id is generated from unique triple below.
    # Django has poor support of multiple column primary key so created this one
    id = models.CharField(max_length=42, primary_key=True)

    # unique triple, these three values have to be unique on Ethereum based chain
    network = models.IntegerField()
    nonce = models.BigIntegerField()
    sender = models.CharField(max_length=42)

    # reported specifically by yagna
    yagna_time_created = models.DateTimeField()
    yagna_time_last_action = models.DateTimeField()
    yagna_time_sent = models.DateTimeField()
    yagna_time_confirmed = models.DateTimeField()
    yagna_starting_gas_price = models.CharField(
        max_length=128, null=True, default=None)
    yagna_maximum_gas_price = models.CharField(
        max_length=128, null=True, default=None)
    yagna_status = models.IntegerField()

    # final transaction hash if payment successful
    final_tx = models.CharField(max_length=70, unique=True)

    # public data reported by yagna, but also possible to be confirmed on chain
    recipient = models.CharField(max_length=42, null=True, default=None)
    gas_used = models.IntegerField(null=True, default=None)
    gas_limit = models.IntegerField(null=True, default=None)
    gas_price = models.CharField(max_length=128, null=True, default=None)

    # not needed for convenience only
    amount_human = models.FloatField(null=True, default=None)
    gas_spent_human = models.FloatField(null=True, default=None)
    gas_price_gwei = models.FloatField(null=True, default=None)

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
    invoice_id = models.UUIDField(primary_key=True)
    amount = models.CharField(max_length=128)
    issuer_id = models.CharField(max_length=42)
    payment_platform = models.CharField(max_length=64)
    agreement = models.ForeignKey('api.Agreement', on_delete=models.CASCADE)
    project = models.ForeignKey('api.Project', on_delete=models.CASCADE)
    linked_payment = models.ForeignKey(
        'api.Payment', on_delete=models.CASCADE, null=True, blank=True)


class Activity(models.Model):
    activity_id = models.UUIDField(primary_key=True)
    provider_node = models.ForeignKey(ProviderNode, on_delete=models.CASCADE)
    requestor_node = models.ForeignKey(
        RequestorAgent, on_delete=models.CASCADE)
    job_name = models.CharField(max_length=64)
    job_quantity = models.FloatField()
    job_unit = models.CharField(max_length=64)
    cpu_time = models.FloatField()
    job_cost = models.FloatField()
    invoice = models.ForeignKey(
        Invoice, null=True, blank=True, on_delete=models.CASCADE)
    agreement = models.ForeignKey(
        Agreement, null=True, blank=True, on_delete=models.CASCADE)
    task_status = models.CharField(max_length=64)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
