from django.urls import path
from .views import (
    HomePageView,
    PetDetailView,
    ReservePetView,
    AddPetView,
    EditPetView,
    DeletePetView,
    AgreementView,
    SheltersListView,
    ShelterDetailView,
    DashboardView,
    UpdateRequestStatusView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home_page"),
    path("pets/<int:pk>/", PetDetailView.as_view(), name="pet_detail"),
    path("pets/<int:pk>/reserve/", ReservePetView.as_view(), name="reserve_pet"),
    path("pets/add/", AddPetView.as_view(), name="add_pet"),
    path("pets/<int:pk>/edit/", EditPetView.as_view(), name="edit_pet"),
    path("pets/<int:pk>/delete/", DeletePetView.as_view(), name="delete_pet"),
    path("agreement/<int:pk>/", AgreementView.as_view(), name="agreement"),
    path("shelters/", SheltersListView.as_view(), name="shelter_list"),
    path("shelters/<int:pk>/", ShelterDetailView.as_view(), name="shelter_detail"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path(
        "requests/<int:pk>/status/",
        UpdateRequestStatusView.as_view(),
        name="update_request_status",
    ),
]
