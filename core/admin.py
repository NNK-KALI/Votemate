from django.contrib import admin
from .models import Aadhaar


class AadhaarAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Aadhaar._meta.fields]
    list_editable = ["is_eligible"]


admin.site.register(Aadhaar, AadhaarAdmin)
