from pyexpat import model
from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    apikey = models.UUIDField(default=uuid.uuid4, editable=True)


class Payment(models.Model):
    tx = models.CharField(max_length=70, unique=True)
    status = models.CharField(max_length=35)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.CharField(max_length=42, null=True, default=None)
    recipient = models.CharField(max_length=42, null=True, default=None)
    glm = models.FloatField(null=True, default=None)
    matic = models.FloatField(null=True, default=None)
    gasUsed = models.BigIntegerField(null=True, default=None)
    gasPrice = models.BigIntegerField(null=True, default=None)
    gasPriceGwei = models.FloatField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Project(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class RequestorNode(models.Model):
    walletAddress = models.CharField(max_length=42)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Provider(models.Model):
    walletAddress = models.CharField(max_length=42)
    name = models.CharField(max_length=128)


class ProviderNode(models.Model):
    providerId = models.CharField(max_length=42)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)


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
    taskStatus = models.CharField(max_length=64)
