from django import forms
from pets.models import Pet, AdoptionRequest, AnimalType, Vaccination  # ← додай Vaccination


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "name",
            "type",
            "breed",
            "age",
            "description",
            "photo",
            "vaccination",
            "price",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            first_type = AnimalType.objects.first()
            if first_type:
                self.fields["type"].initial = first_type.pk

            first_vaccine = Vaccination.objects.first()
            if first_vaccine:
                self.fields["vaccination"].initial = first_vaccine.pk

        self.fields["vaccination"].required = False
        self.fields["vaccination"].empty_label = "— No vaccination info —"

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is not None and age < 0:
            raise forms.ValidationError("Age must be 0 or greater.")
        return age

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError("Price must be 0 or greater.")
        return price


class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Introduce yourself and tell us why you'd like to adopt this pet...",
                }
            ),
        }
        labels = {
            "message": "Your message to the owner (optional)",
        }
