from django import forms
from users.models import BreederShelterProfile

INPUT_CLASS = "w-full border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-400"


class BreederShelterProfileForm(forms.ModelForm):
    class Meta:
        model = BreederShelterProfile
        fields = ["name", "city", "phone", "description", "is_shelter"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Organization name"}),
            "city": forms.Select(attrs={"class": INPUT_CLASS}),
            "phone": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "+380..."}),
            "description": forms.Textarea(attrs={
                "class": INPUT_CLASS, "rows": 4,
                "placeholder": "Tell us about your shelter or breeding program...",
            }),
        }