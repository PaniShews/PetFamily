from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User

INPUT_CLASS = "w-full border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-400"


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": INPUT_CLASS,
        "placeholder": "Email",
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": INPUT_CLASS,
        "placeholder": "First name",
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": INPUT_CLASS,
        "placeholder": "Last name",
    }))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Username",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": INPUT_CLASS, "placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"class": INPUT_CLASS, "placeholder": "Confirm password"})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": INPUT_CLASS, "placeholder": "Username"})
        self.fields["password"].widget.attrs.update({"class": INPUT_CLASS, "placeholder": "Password"})


RegularUserRegistrationForm = RegisterForm


class OrganizationRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": INPUT_CLASS, "placeholder": "Email",
    }))
    org_name = forms.CharField(max_length=100, label="Organization name", widget=forms.TextInput(attrs={
        "class": INPUT_CLASS, "placeholder": "Shelter or kennel name",
    }))
    phone = forms.CharField(max_length=20, required=False, label="Phone number", widget=forms.TextInput(attrs={
        "class": INPUT_CLASS, "placeholder": "+38 000 000 0000",
    }))
    description = forms.CharField(required=False, label="About your organization", widget=forms.Textarea(attrs={
        "class": INPUT_CLASS, "placeholder": "Tell adopters about your organization…", "rows": 3,
    }))
    is_shelter = forms.BooleanField(
        required=False,
        label="We are a shelter (animals are free)",
        help_text="Leave unchecked if you are a breeder.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Username"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": INPUT_CLASS, "placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"class": INPUT_CLASS, "placeholder": "Confirm password"})