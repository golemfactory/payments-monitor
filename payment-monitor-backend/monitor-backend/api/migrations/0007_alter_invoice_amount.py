# Generated by Django 3.2.13 on 2022-04-22 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_activity_usage_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='amount',
            field=models.FloatField(max_length=128),
        ),
    ]
