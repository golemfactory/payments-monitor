from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging
from celery.schedules import crontab


logger = logging.getLogger("Celery")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')


# @app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     from api.tasks import monitor_requestors, monitor_rpc, monitor_db, monitor_load, monitor_proxies, monitor_known_miners
#     sender.add_periodic_task(
#         30.0,
#         monitor_requestors.s(),
#         queue='default',
#         options={
#             'queue': 'default',
#             'routing_key': 'default'}
#     )
#     sender.add_periodic_task(
#         30.0,
#         monitor_rpc.s(),
#         queue='default',
#         options={
#             'queue': 'default',
#             'routing_key': 'default'}
#     )
#     sender.add_periodic_task(
#         30.0,
#         monitor_db.s(),
#         queue='default',
#         options={
#             'queue': 'default',
#             'routing_key': 'default'}
#     )
#     sender.add_periodic_task(
#         30.0,
#         monitor_load.s(),
#         queue='default',
#         options={
#             'queue': 'default',
#             'routing_key': 'default'}
#     )
#     sender.add_periodic_task(
#         30.0,
#         monitor_proxies.s(),
#         queue='default',
#         options={
#             'queue': 'default',
#             'routing_key': 'default'}
#     )
#     sender.add_periodic_task(
#         30.0,
#         monitor_known_miners.s(),
#         queue='default',
#         options={
#             'queue': 'default',
#             'routing_key': 'default'}
#     )


app.conf.task_default_queue = 'default'
app.conf.broker_url = 'redis://redis:6379/0'
app.conf.result_backend = 'redis://redis:6379/0'
app.conf.task_routes = {'app.tasks.default': {
    'queue': 'default'}}
