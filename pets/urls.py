from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("pets/<int:pk>/", views.pet_detail, name="pet_detail"),
    path("pets/<int:pk>/reserve/", views.reserve_pet, name="reserve_pet"),
    path("pets/<int:pk>/reserve/", views.reserve_pet, name="make_request"),  # alias for pet_detail.html
    path("pets/add/", views.add_pet, name="add_pet"),
    path("pets/<int:pk>/edit/", views.edit_pet, name="edit_pet"),
    path("pets/<int:pk>/delete/", views.delete_pet, name="delete_pet"),
    path("agreement/<int:pk>/", views.agreement, name="agreement"),
    path("shelters/", views.shelters_list, name="shelter_list"),
    path("shelters/<int:pk>/", views.shelter_detail, name="shelter_detail"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("requests/<int:pk>/status/", views.update_request_status, name="update_request_status"),
]