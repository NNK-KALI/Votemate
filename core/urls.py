from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("results/", views.results, name="results"),
    path("add_contestant", views.add_contestant, name="add_contestant"),
    path("contestants_details/", views.contestants_details, name="contestants_details"),
    path("change_state/", views.change_state, name="change_state"),
    path("add_voters/", views.add_voters, name="add_voters"),
    path("voter_registration", views.voter_registration, name="voter_registration"),
    path("verify_otp/", views.verify_otp, name="verify_otp"),
    path("voting_area/", views.voting_area, name="voting_area"),
]
