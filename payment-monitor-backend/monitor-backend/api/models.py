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


user_life_on_golem
user_chess_on_golem
user_both


life on golem 1
chess on golem


class Project
    id
    name


RequestorNode
    address
    project



#dont need to be separate info for now but maybe we want to make some annotations
Provider
   address
   comment


ProviderNode
   id 
   provider
   info_about_pc
   
Activity:
    providerNode
    requestorNode
    "job_name": "test_fixing_primes",
    "job_quantity": 10.0,
    "job_unit": "primes",
    "job_time": 5.613140096618357,
    "cpu_time": 2.0531400966183577,
    "job_cost": 25.214028985507248,
    payment// it could be null
    task_status
