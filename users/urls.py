from django.urls import path
from users.views.auth import (
    RegisterChoiceView,
    RegisterUserView,
    RegisterOrganizationView,
    LoginView,
    LogoutView,
)
from users.views.profile import ProfileView, MyRequestsView

urlpatterns = [
    path("register/", RegisterChoiceView.as_view(), name="register"),
    path("register/user/", RegisterUserView.as_view(), name="register_user"),
    path(
        "register/organization/",
        RegisterOrganizationView.as_view(),
        name="register_organization",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("my-requests/", MyRequestsView.as_view(), name="my_requests"),
]
