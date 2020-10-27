from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as DefaultUserCreationForm


class UserCreationForm(DefaultUserCreationForm):

    class Meta:
        fields = ("username",)
        model = get_user_model() 
