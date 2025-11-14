from django.contrib import admin
from .models import User, Client, Domain

# tenant model.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'domain_url', 'on_trial', 'paid_until', 'created_on')

# domain model
@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
