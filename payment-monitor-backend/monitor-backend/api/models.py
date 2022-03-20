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
