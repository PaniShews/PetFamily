from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from users.forms.profile_form import BreederShelterProfileForm
from pets.models import AdoptionRequest


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "registration/profile.html"
    form_class = BreederShelterProfileForm
    success_url = reverse_lazy("profile")

    def get_profile(self):
        return getattr(self.request.user, "organization_profile", None)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile = self.get_profile()
        if profile:
            kwargs["instance"] = profile
        if self.request.method == "POST":
            kwargs["files"] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        p = form.save(commit=False)
        p.user = self.request.user
        p.save()
        messages.success(self.request, "Profile saved!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.get_profile()
        return ctx


class MyRequestsView(LoginRequiredMixin, ListView):
    template_name = "pets/my_requests.html"
    context_object_name = "adoption_requests"

    def get_queryset(self):
        return (
            AdoptionRequest.objects.filter(user=self.request.user)
            .select_related("pet", "pet__owner")
            .order_by("-created_at")
        )
