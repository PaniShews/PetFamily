from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from .forms.pet_form import PetForm, AdoptionRequestForm
from .models import Pet, AdoptionRequest, AnimalType
from users.models import BreederShelterProfile


class OrgRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, "organization_profile"):
            messages.error(request, "Only shelters and breeders can access this page.")
            return redirect("home_page")
        return super().dispatch(request, *args, **kwargs)

    def get_profile(self):
        return self.request.user.organization_profile


class HomePageView(ListView):
    model = Pet
    template_name = "pets/home_page.html"
    context_object_name = "pets"

    def get_queryset(self):
        qs = Pet.objects.filter(is_available=True).select_related("owner", "type")
        q = self.request.GET.get("q")
        animal_type = self.request.GET.get("type")
        kind = self.request.GET.get("kind")

        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(breed__icontains=q)
        if animal_type:
            qs = qs.filter(type__id=animal_type)
        if kind == "shelter":
            qs = qs.filter(owner__is_shelter=True)
        elif kind == "breeder":
            qs = qs.filter(owner__is_shelter=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["animal_types"] = AnimalType.objects.all()
        ctx["search"] = self.request.GET.get("q", "")
        ctx["selected_type"] = self.request.GET.get("type", "")
        ctx["kind"] = self.request.GET.get("kind", "")
        return ctx


class PetDetailView(DetailView):
    model = Pet
    template_name = "pets/pet_detail.html"
    context_object_name = "pet"


class SheltersListView(ListView):
    model = BreederShelterProfile
    template_name = "pets/shelter_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        return BreederShelterProfile.objects.select_related("user", "city").order_by(
            "name"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx["shelters"] = qs.filter(is_shelter=True)
        ctx["breeders"] = qs.filter(is_shelter=False)
        return ctx


class ShelterDetailView(DetailView):
    model = BreederShelterProfile
    template_name = "pets/shelter_detail.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pets = Pet.objects.filter(owner=self.object).select_related("type")
        ctx["available_pets"] = pets.filter(is_available=True)
        ctx["adopted_pets"] = pets.filter(is_available=False)
        return ctx


class ReservePetView(LoginRequiredMixin, View):
    template_name = "pets/make_request.html"

    def get_pet(self, pk):
        return get_object_or_404(Pet, pk=pk, is_available=True)

    def get(self, request, pk):
        pet = self.get_pet(pk)
        existing = AdoptionRequest.objects.filter(user=request.user, pet=pet).first()
        if existing:
            messages.info(request, "You have already submitted a request for this pet.")
            return redirect("agreement", pk=existing.pk)
        return self._render(request, pet, AdoptionRequestForm())

    def post(self, request, pk):
        pet = self.get_pet(pk)
        form = AdoptionRequestForm(request.POST)
        if form.is_valid():
            adoption = form.save(commit=False)
            adoption.user = request.user
            adoption.pet = pet
            adoption.agreed_price = pet.price if not pet.is_free else None
            adoption.save()
            pet.is_available = False
            pet.save()
            messages.success(
                request, f"Your request for {pet.name} has been submitted!"
            )
            return redirect("agreement", pk=adoption.pk)
        return self._render(request, pet, form)

    def _render(self, request, pet, form):
        from django.shortcuts import render

        return render(request, self.template_name, {"pet": pet, "form": form})


class AgreementView(LoginRequiredMixin, DetailView):
    model = AdoptionRequest
    template_name = "pets/agreement.html"
    context_object_name = "adoption"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        adoption = self.get_object()
        is_owner = (
            request.user == adoption.pet.owner.user if adoption.pet.owner else False
        )
        if adoption.user != request.user and not is_owner:
            messages.error(request, "You don't have permission to view this agreement.")
            return redirect("home_page")
        return response


class DashboardView(OrgRequiredMixin, TemplateView):
    template_name = "pets/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = self.get_profile()
        ctx["profile"] = profile
        ctx["pets"] = Pet.objects.filter(owner=profile).order_by("-created_at")
        ctx["adoption_requests"] = (
            AdoptionRequest.objects.filter(pet__owner=profile)
            .select_related("user", "pet")
            .order_by("-created_at")
        )
        return ctx


class AddPetView(OrgRequiredMixin, CreateView):
    form_class = PetForm
    template_name = "pets/add_pet.html"
    success_url = reverse_lazy("dashboard")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.get_profile().is_shelter:
            form.fields["price"].widget = form.fields["price"].hidden_widget()
            form.fields["price"].required = False
        return form

    def form_valid(self, form):
        profile = self.get_profile()
        form.instance.owner = profile
        if profile.is_shelter:
            form.instance.price = None
        messages.success(self.request, f"{form.instance.name} has been added!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.get_profile()
        return ctx


class EditPetView(OrgRequiredMixin, UpdateView):
    form_class = PetForm
    template_name = "pets/add_pet.html"
    success_url = reverse_lazy("dashboard")

    def get_object(self, queryset=None):
        return get_object_or_404(Pet, pk=self.kwargs["pk"], owner=self.get_profile())

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.get_profile().is_shelter:
            form.fields["price"].widget = form.fields["price"].hidden_widget()
            form.fields["price"].required = False
        return form

    def form_valid(self, form):
        if self.get_profile().is_shelter:
            form.instance.price = None
        messages.success(self.request, f"{form.instance.name} has been updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.get_profile()
        ctx["edit"] = True
        ctx["pet"] = self.get_object()
        return ctx


class DeletePetView(OrgRequiredMixin, DeleteView):
    template_name = "pets/dashboard.html"
    success_url = reverse_lazy("dashboard")

    def get_object(self, queryset=None):
        return get_object_or_404(Pet, pk=self.kwargs["pk"], owner=self.get_profile())

    def form_valid(self, form):
        messages.success(self.request, f"{self.get_object().name} has been removed.")
        return super().form_valid(form)


class UpdateRequestStatusView(OrgRequiredMixin, View):

    def post(self, request, pk):
        adoption = get_object_or_404(AdoptionRequest, pk=pk)
        profile = self.get_profile()

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
