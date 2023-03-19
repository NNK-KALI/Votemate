from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    """
    A Custom form for creating new users.
    """

    class Meta:
        model = get_user_model()
        fields = ["email"]


# class CustomUserLoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields.pop('username')

#     email = forms.CharField(max_length=254, widget=forms.EmailInput(attrs={'autofocus': True}))

#     class Meta:
#         model = CustomUser
#         fields = ('email', 'password')
