from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BreederShelterProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(BreederShelterProfile)
class BreederShelterProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "is_shelter", "city", "phone"]
    list_filter = ["is_shelter"]
    search_fields = ["name", "user__username"]