from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User


class RegularUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class OrganizationRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    org_name = forms.CharField(max_length=100, label="Organization name")
    phone = forms.CharField(max_length=20, required=False, label="Phone number")
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="About your organization",
    )
    is_shelter = forms.BooleanField(
        required=False,
        label="We are a shelter (animals are free)",
        help_text="Leave unchecked if you are a breeder (animals have a price).",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
