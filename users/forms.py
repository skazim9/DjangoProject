from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]