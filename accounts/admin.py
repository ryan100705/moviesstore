from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "state", "region_code")
    search_fields = ("user__username", "city", "state", "region_code")
