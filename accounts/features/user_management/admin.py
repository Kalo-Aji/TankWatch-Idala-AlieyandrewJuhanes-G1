from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.features.user_management.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "contact_number",
        "is_staff",
    ]
    list_filter = ["role", "is_staff", "is_active", "date_joined"]
    fieldsets = UserAdmin.fieldsets + (
        ("TankWatch Profile", {"fields": ["role", "contact_number"]}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("TankWatch Profile", {"fields": ["role", "contact_number"]}),
    )
