from django.contrib import admin
from .models import Paste

@admin.register(Paste)
class PasteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "expires_at",
        "max_views",
        "current_views",
    )

    readonly_fields = ("id", "created_at", "current_views")

# Register your models here.
