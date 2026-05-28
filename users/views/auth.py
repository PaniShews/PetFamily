from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from users.forms.auth_forms import RegularUserRegistrationForm, OrganizationRegistrationForm


def register_choice(request):
    return render(request, "registration/register_choice.html")


def register_user(request):
    if request.user.is_authenticated:
        return redirect("home_page")

    if request.method == "POST":
        form = RegularUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect("home_page")
    else:
        form = RegularUserRegistrationForm()

    return render(request, "registration/register_user.html", {"form": form})


def register_organization(request):
    if request.user.is_authenticated:
        return redirect("home_page")
    if request.method == "POST":
        form = OrganizationRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from users.models import BreederShelterProfile
            BreederShelterProfile.objects.create(
                user=user,
                name=form.cleaned_data["org_name"],
                phone=form.cleaned_data.get("phone", ""),
                description=form.cleaned_data.get("description", ""),
                is_shelter=form.cleaned_data.get("is_shelter", False),
            )
            login(request, user)
            messages.success(request, f"Welcome! Your organization profile has been created.")
            return redirect("dashboard")
    else:
        form = OrganizationRegistrationForm()

    return render(request, "registration/register_organization.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home_page")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "home_page")
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect("home_page")