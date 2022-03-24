from django.db import models


class Invoice(models.Model):
    amount = models.FloatField()
    invoice_id = models.UUIDField()
    issuer_id = models.CharField(max_length=42)
    payment_platform = models.CharField(max_length=64)
    agreement = models.ForeignKey('api.Agreement', on_delete=models.CASCADE)
    project = models.ForeignKey('api.Project', on_delete=models.CASCADE)
    linked_payment = models.ForeignKey(
        'api.Payment', on_delete=models.CASCADE, null=True, blank=True)
