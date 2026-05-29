from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView

from users.forms.auth_forms import (
    RegularUserRegistrationForm,
    OrganizationRegistrationForm,
)
from users.models import BreederShelterProfile


class RegisterChoiceView(TemplateView):
    template_name = "registration/register_choice.html"


class RegisterUserView(FormView):
    template_name = "registration/register_user.html"
    form_class = RegularUserRegistrationForm
    success_url = reverse_lazy("home_page")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home_page")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, f"Welcome, {user.first_name}! Your account has been created."
        )
        return super().form_valid(form)


class RegisterOrganizationView(FormView):
    template_name = "registration/register_organization.html"
    form_class = OrganizationRegistrationForm
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home_page")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        BreederShelterProfile.objects.create(
            user=user,
            name=form.cleaned_data["org_name"],
            phone=form.cleaned_data.get("phone", ""),
            description=form.cleaned_data.get("description", ""),
            is_shelter=form.cleaned_data.get("is_shelter", False),
        )
        login(self.request, user)
        messages.success(
            self.request, "Welcome! Your organization profile has been created."
        )
        return super().form_valid(form)


class LoginView(FormView):
    template_name = "registration/login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy("home_page")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home_page")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["data"] = self.request.POST or None
        return kwargs

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Welcome back, {user.username}!")
        next_url = self.request.GET.get("next", "home_page")
        return redirect(next_url)


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You've been logged out.")
        return redirect("home_page")
