from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import UserCreateView, email_verification, password_reset_request, password_reset_confirm, \
    password_reset_complete, password_reset_invalid, password_reset_done


app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email_confirm/<str:token>/", email_verification, name="email_confirm"),
    path("password_reset/", password_reset_request, name="password_reset"),
    path("password_reset_done/", password_reset_done, name="password_reset_done"),
    path("password_reset_confirm/<str:uid64>/<str:token>/", password_reset_confirm, name="password_reset_confirm"),
    path("password_reset_complete/", password_reset_complete, name="password_reset_complete"),
    path("password_reset_invalid/", password_reset_invalid, name="password_reset_invalid"),
]