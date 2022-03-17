from django.contrib import admin
from .models import User, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
