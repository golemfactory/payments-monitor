from audioop import add
from aiohttp import request
from core.celery import app
from celery import Celery
import json
import requests
from datetime import datetime
import os
import time
from api.models.models import Payment, User
from .utils import get_erc20_transaction_details
from web3 import Web3


@app.task(name='check_tx_status')
def check_tx_status(tx, key):
    test = transaction_details = get_erc20_transaction_details(tx)
    user = User.objects.get(apikey=key)
    if test['transaction_found'] == False:
        Payment.objects.create(
            user=user, tx=tx, status="Transaction not found")
    elif test['transaction_receipt_found'] == False:
        Payment.objects.create(
            user=user, tx=tx, status="Receipt not found")
    elif test['failure_to_process'] == True:
        Payment.objects.create(
            user=user, tx=tx, status="Failed to process")
    else:
        payment = Payment.objects.create(
            user=user, tx=tx, status="confirmed", sender=test['from'], recipient=test['to'],  glm=test['human_value'], matic=test['human_gas_cost'], gasUsed=test['gas_used'], gasPrice=test['gas_price'], gasPriceGwei=test['gas_price_gwei'])
