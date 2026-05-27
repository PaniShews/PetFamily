from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms.pet_form import PetForm, AdoptionRequestForm
from .models import Pet, AdoptionRequest, AnimalType
from users.models import BreederShelterProfile


def home_page(request):
    pets = Pet.objects.filter(is_available=True).select_related("owner", "type")

    animal_type = request.GET.get("type")
    search = request.GET.get("q")
    kind = request.GET.get("kind")

    if animal_type:
        pets = pets.filter(type__id=animal_type)
    if search:
        pets = pets.filter(name__icontains=search) | pets.filter(breed__icontains=search)
    if kind == "shelter":
        pets = pets.filter(owner__is_shelter=True)
    elif kind == "breeder":
        pets = pets.filter(owner__is_shelter=False)


    animal_types = AnimalType.objects.all()

    return render(request, "pets/home_page.html", {
        "pets": pets,
        "animal_types": animal_types,
        "selected_type": animal_type,
        "search": search,
        "kind": kind,
    })


def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    return render(request, "pets/pet_detail.html", {"pet": pet})


@login_required
def reserve_pet(request, pk):
    pet = get_object_or_404(Pet, pk=pk, is_available=True)

    existing = AdoptionRequest.objects.filter(user=request.user, pet=pet).first()
    if existing:
        messages.info(request, "You have already submitted a request for this pet.")
        return redirect("agreement", pk=existing.pk)

    if request.method == "POST":
        form = AdoptionRequestForm(request.POST)
        if form.is_valid():
            adoption = form.save(commit=False)
            adoption.user = request.user
            adoption.pet = pet
            adoption.agreed_price = pet.price if not pet.is_free else None
            adoption.save()

            pet.is_available = False
            pet.save()

            messages.success(request, f"Your request for {pet.name} has been submitted!")
            return redirect("agreement", pk=adoption.pk)
    else:
        form = AdoptionRequestForm()

    return render(request, "pets/reserve_pet.html", {"pet": pet, "form": form})


@login_required
def agreement(request, pk):
    adoption = get_object_or_404(AdoptionRequest, pk=pk)

    is_owner = (
        request.user == adoption.pet.owner.user
        if adoption.pet.owner
        else False
    )
    if adoption.user != request.user and not is_owner:
        messages.error(request, "You don't have permission to view this agreement.")
        return redirect("home_page")

    return render(request, "pets/agreement.html", {"adoption": adoption})


def shelters_list(request):
    profiles = BreederShelterProfile.objects.select_related("user", "city").order_by("name")
    shelters = profiles.filter(is_shelter=True)
    breeders = profiles.filter(is_shelter=False)
    return render(request, "pets/shelter_list.html", {
        "shelters": shelters,
        "breeders": breeders,
    })


def shelter_detail(request, pk):
    profile = get_object_or_404(BreederShelterProfile, pk=pk)
    pets = Pet.objects.filter(owner=profile).select_related("type")
    available = pets.filter(is_available=True)
    adopted = pets.filter(is_available=False)
    return render(request, "pets/shelter_detail.html", {
        "profile": profile,
        "available_pets": available,
        "adopted_pets": adopted,
    })


@login_required
def dashboard(request):
    try:
        profile = request.user.organization_profile
    except Exception:
        messages.error(request, "You need an organization profile to access the dashboard.")
        return redirect("home_page")

    pets = Pet.objects.filter(owner=profile).order_by("-created_at")
    requests = AdoptionRequest.objects.filter(pet__owner=profile).select_related("user", "pet").order_by("-created_at")

    return render(request, "pets/dashboard.html", {
        "profile": profile,
        "pets": pets,
        "adoption_requests": requests,
    })


@login_required
def add_pet(request):
    # не забудь помилки впрехать
    try:
        profile = request.user.organization_profile
    except Exception:
        messages.error(request, "Only shelters and breeders can add pets.")
        return redirect("home_page")

    if request.method == "POST":
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = profile

            if profile.is_shelter:
                pet.price = None
            pet.save()
            messages.success(request, f"{pet.name} has been added!")
            return redirect("dashboard")
    else:
        form = PetForm()

        if profile.is_shelter:
            form.fields["price"].widget = form.fields["price"].hidden_widget()
            form.fields["price"].required = False

    return render(request, "pets/add_pet.html", {"form": form, "profile": profile})


@login_required
def edit_pet(request, pk):
    try:
        profile = request.user.organization_profile
    except Exception:
        return redirect("home_page")

    pet = get_object_or_404(Pet, pk=pk, owner=profile)

    if request.method == "POST":
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            updated = form.save(commit=False)
            if profile.is_shelter:
                updated.price = None
            updated.save()
            messages.success(request, f"{pet.name} has been updated.")
            return redirect("dashboard")
    else:
        form = PetForm(instance=pet)
        if profile.is_shelter:
            form.fields["price"].widget = form.fields["price"].hidden_widget()
            form.fields["price"].required = False

    return render(request, "pets/add_pet.html", {"form": form, "profile": profile, "edit": True, "pet": pet})


@login_required
def delete_pet(request, pk):
    try:
        profile = request.user.organization_profile
    except Exception:
        return redirect("home_page")

    pet = get_object_or_404(Pet, pk=pk, owner=profile)
    if request.method == "POST":
        pet_name = pet.name
        pet.delete()
        messages.success(request, f"{pet_name} has been removed.")
    return redirect("dashboard")


@login_required
def update_request_status(request, pk):
    adoption = get_object_or_404(AdoptionRequest, pk=pk)
    try:
        profile = request.user.organization_profile
    except Exception:
        return redirect("home_page")

    if adoption.pet.owner != profile:
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    new_status = request.POST.get("status")
    if new_status in ["approved", "rejected"]:
        adoption.status = new_status
        adoption.save()
        if new_status == "rejected":

            adoption.pet.is_available = True
            adoption.pet.save()
        messages.success(request, f"Request {new_status}.")

    return redirect("dashboard")
