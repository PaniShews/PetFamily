from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.forms.profile_form import BreederShelterProfileForm
from pets.models import AdoptionRequest


@login_required
def profile_view(request):
    profile = getattr(request.user, "organization_profile", None)

    if request.method == "POST":
        if profile:
            form = BreederShelterProfileForm(request.POST, request.FILES, instance=profile)
        else:
            form = BreederShelterProfileForm(request.POST, request.FILES)

        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.save()
            messages.success(request, "Profile saved!")
            return redirect("profile")
    else:
        form = BreederShelterProfileForm(instance=profile) if profile else BreederShelterProfileForm()

    return render(request, "registration/profile.html", {
        "form": form,
        "profile": profile,
    })


@login_required
def my_requests(request):
    adoption_requests = AdoptionRequest.objects.filter(
        user=request.user
    ).select_related("pet", "pet__owner").order_by("-created_at")

    return render(request, "pets/my_requests.html", {
        "adoption_requests": adoption_requests,
    })
