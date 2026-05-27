from django.urls import path
from users.views import auth, profile

urlpatterns = [
    path("register/", auth.register_choice, name="register"),
    path("register/user/", auth.register_user, name="register_user"),
    path("register/organization/", auth.register_organization, name="register_organization"),
    path("login/", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("profile/", profile.profile_view, name="profile"),
    path("my-requests/", profile.my_requests, name="my_requests"),
]