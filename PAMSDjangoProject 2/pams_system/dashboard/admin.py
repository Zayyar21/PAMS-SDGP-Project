from django.contrib import admin
from .models import Apartment, Tenant, MaintenanceRequest, Complaint, Payment, Profile


# Apartment
@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):

    list_display = ("id", "rent", "rooms")
    search_fields = ("id",)
    list_filter = ("rooms",)


# Tenant
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):

    list_display = ("user", "apartment", "lease_start", "lease_end")
    search_fields = ("user__username",)


# Maintenance
@admin.register(MaintenanceRequest)
class MaintenanceAdmin(admin.ModelAdmin):

    list_display = ("user", "issue_type", "priority", "status", "created_at")
    list_filter = ("status", "priority")


# Complaint
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = ("user", "category", "status", "date")
    list_filter = ("status", "category")


admin.site.register(Payment)
admin.site.register(Profile)