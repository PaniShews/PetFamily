from django import forms
from pets.models import Pet, AdoptionRequest


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
