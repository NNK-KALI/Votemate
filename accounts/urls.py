from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    # The login is handled by the default urls provided by django.
    # check votemate.urls.py for more info
]
