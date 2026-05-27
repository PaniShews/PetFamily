from django.contrib import admin
from .models import City, Vaccination, AnimalType, Pet, AdoptionRequest


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ["name", "certificate"]


@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ["name", "breed", "type", "age", "owner", "is_available", "price"]
    list_filter = ["type", "is_available", "owner__is_shelter"]
    search_fields = ["name", "breed"]


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "pet", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__username", "pet__name"]
