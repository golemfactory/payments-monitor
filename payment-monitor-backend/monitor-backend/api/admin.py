from django.contrib import admin
from .models import User, Payment, Invoice, Project, RequestorAgent, Provider, ProviderNode, Agreement, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.site.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.site.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.site.register(RequestorAgent)
class RequestorAgentAdmin(admin.ModelAdmin):
    pass


@admin.site.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    pass


@admin.site.register(ProviderNode)
class ProviderNodeAdmin(admin.ModelAdmin):
    pass


@admin.site.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    pass
