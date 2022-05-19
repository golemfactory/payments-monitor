from rest_framework import serializers
from .models import Payment, Activity, Logs


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = '__all__'


class LogsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logs
        fields = '__all__'
