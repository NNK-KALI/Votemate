from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from smart_contracts.contest import Contest
from django.contrib import messages
from .models import Aadhaar
from termcolor import colored
from django.conf import settings
from django.core.mail import send_mail
import random
import sys


# This is to prevent creating the contest object (which connects to blockchain) when views is
# imported into other file (ex: when makemigrations )
# So, we are checking the arguments passed in the command line and checking if runserver is passed
# as an argument and only create object when it's passed. so, object is created only when runserver is called.
# Couldn't find a better solution than this.
# Change this if condition based on your use case or needs (ex: if you want to )
if "runserver" in sys.argv:
    contest = Contest(True)


def home(request):
    return render(request, "home.html")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def change_state(request):
    if request.method == "POST":
        state = request.POST.get("change_state")
        tx_report = contest.set_phase(state)
        print(tx_report)
        if tx_report["status"] == True:
            messages.success(request, f"changed phase to {state} successfully")
        else:
            messages.error(request, "Transaction failed. Note: can't revert to back")
        return redirect("change_state")

    current_state = contest.get_current_phase()
    context = {"current_state": current_state}
    return render(request, "change_state.html", context=context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_voters(request):
    if request.method == "POST":
        # Get the list of public keys
        public_keys = request.POST.getlist("public_keys")
        # store the public keys that are successfully registered
        registered_public_keys = []
        updated_values_count = 0  # To make count of successfull blockchain transactions
        # loop over the public keys and make blockchain transactions and store keys
        # with successfull transactions
        for key in public_keys:
            tx_report = contest.voter_registration(key)
            if tx_report["status"] == True:
                updated_values_count += 1
                registered_public_keys.append(key)
        # set has_registered to true for all the public keys that are sucessfully registered
        try:
            Aadhaar.objects.filter(eth_public_key__in=registered_public_keys).update(
                has_registered=True
            )
        except Exception as e:
            print(colored(e, "red"))
        messages.success(request, f"updated {updated_values_count} records.")

    # Render the template with the list of voter details
    voters_details = []
    registered_voters = (
        Aadhaar.objects.filter(has_registered=False)
        .filter(is_eligible=True)
        .filter(eth_public_key__isnull=False)
    )
    for registered_voter in registered_voters:
        voters_details.append(
            {
                "eth_public_key": registered_voter.eth_public_key,
                "aadhaar_number": registered_voter.aadhaar_number,
            }
        )
    context = {"voters_details": [voter_details for voter_details in voters_details]}
    return render(request, "add_voters.html", context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_contestant(request):
    if request.method == "POST":
        # get data from Form
        contestant_name = request.POST.get("contestant_name")
        contestant_age = int(request.POST.get("contestant_age"))
        contestant_party = request.POST.get("contestant_party")
        contestant_qualification = request.POST.get("contestant_qualification")
        # send data to blockchain, it returns a dict with two items(success and receipt)
        tx_report = contest.add_contestant(
            name=contestant_name,
            age=contestant_age,
            party=contestant_party,
            qualification=contestant_qualification,
        )
        if tx_report["status"] == True:
            messages.success(request, "Contestant Added successfully.")
        else:
            messages.error(request, "Transaction failed. Note: check phase")

    return render(request, "add_contestant.html")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def contestants_details(request):
    contestants_list = contest.get_contestants()
    context = {
        "contestants_list": contestants_list,
    }
    return render(request, "contestants_details.html", context=context)


@login_required
def voter_registration(request):
    if request.method == "POST":
        aadhaar_number = request.POST.get("aadhaar_number")
        public_key = request.POST.get("eth_public_key")
        # check if eth_public_key is already present in the database
        if Aadhaar.objects.filter(eth_public_key__in=public_key) != None:
            messages.error(request, "public key is already present in the database.")
        else:
            # Get the record from the aadhaar database using the user's email
            try:
                voter = Aadhaar.objects.get(email=request.user.email)
                # If we receive an object(i.e user with this email is present in Aadhaar table)
                # then check if the user entered aadhaar number and aadhar number linked with
                # user email in the Aadhar tabel in database
                if voter is not None:
                    if aadhaar_number == voter.aadhaar_number:
                        # Check for Age(MOST IMPORTANT)
                        if voter.age >= 18:
                            # Generate OTP
                            otp = str(random.randint(100000, 999999))
                            # Send OTP to user's email
                            send_mail(
                                "OTP Verification",
                                f"Your OTP for Votemate is: {otp}",
                                settings.EMAIL_HOST_USER,
                                [request.user.email],
                                fail_silently=False,
                            )
                            # Store OTP in session
                            request.session["otp"] = otp
                            request.session["aadhaar_number"] = aadhaar_number
                            request.session["public_key"] = public_key
                            # Redirect to OTP verification page
                            return render(request, "verify_otp.html")
                        else:
                            messages.error(request, "Under Age, Not eligible for voting.")
                    else:
                        messages.error(
                            request, "Aadhaar Number didn't match with the registered email"
                        )
            except Aadhaar.DoesNotExist as e:
                print(e)
                messages.error(
                    request, "No record found with this email in Aadhaar Database"
                )
            except Exception as e:
                print(e)
                messages.error(
                    request, "some error occured. make sure the details are correct"
                )

    voter = Aadhaar.objects.get(email=request.user.email)
    already_registered = voter.is_eligible
    context = {"already_registered": already_registered}
    return render(request, "voter_registration.html", context=context)


@login_required
def verify_otp(request):
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        # Get OTP and user details from session
        otp = request.session.get("otp")
        aadhaar_number = request.session.get("aadhaar_number")
        public_key = request.session.get("public_key")
        if otp_entered == otp:
            # Register the user(set is_eligible=True and update eth_public_key with user submited key in database)
            update_is_eligible = Aadhaar.objects.filter(
                aadhaar_number=aadhaar_number
            ).update(is_eligible=True)
            update_eth_public_key = Aadhaar.objects.filter(
                aadhaar_number=aadhaar_number
            ).update(eth_public_key=public_key)
            if update_is_eligible == True and update_eth_public_key == True:
                messages.success(request, "Registered Successfully")
            # Delete OTP and user details from session
            del request.session["otp"]
            del request.session["aadhaar_number"]
            del request.session["public_key"]
            # Redirect to home page
            return redirect("home")
        else:
            messages.error(request, "Invalid OTP")
    return render(request, "verify_otp.html")


@login_required
def results(request):
    # make a request to the blockchain to get the contestants count, registered voters, total_votes_count
    contestants_count = contest.get_contestants_count()
    registered_voters_count = contest.get_voters_count()
    total_votes_count = contest.get_votes_count()
    # Get current phase
    current_phase = contest.get_current_phase()
    # check the phase
    if current_phase == "results":
        # If results phase
        # Get the winner
        # The get_winner_ids returns a list. If list length is greater than one then it's a draw.
        winners_id = contest.get_winner_ids()
        # Get the length of the winners list.
        winners_count = len(winners_id)
        # Get the contestants data form the blockchain
        contestants = contest.get_contestants()
        # list to store the details of the winner/winners
        winners = []
        # Loop over the contestants and check if their id is in the winners_id list and append
        for contestant in contestants:
            if contestant["id"] in winners_id:
                winners.append(contestant)
        # Context dictonary
        context = {
            "contestants_count": contestants_count,  # int
            "registered_voters_count": registered_voters_count,  # int
            "total_votes_count": total_votes_count,  # int
            "winners_count": winners_count,  # int
            "winners": winners,  # winners list -> python list
            "current_phase": current_phase,  # string
        }
    else:
        context = {
            "contestants_count": contestants_count,  # int
            "registered_voters_count": registered_voters_count,  # int
            "total_votes_count": total_votes_count,  # int,
            "current_phase": current_phase,
        }
    print(context)
    return render(request, "results.html", context=context)


@login_required()
def voting_area(request):
    if request.method == "POST":
        # Check for voting phase
        if contest.get_current_phase() == "voting":
            # Extract data form form
            contestant_id = int(request.POST.get("contestant_id"))
            voter_private_key = request.POST.get("private_key")
            print(contestant_id)
            print(voter_private_key)
            # Convert the private key of the user to public key using the helper function.
            public_key = contest.private_key_to_account_address(voter_private_key)
            # And check if the public key matches with the user's registered public key.
            if (
                Aadhaar.objects.get(email=request.user.email).eth_public_key
                == public_key
            ):
                # If matches, Continue voting.
                # transacation for vote
                tx_report = contest.vote(contestant_id, voter_private_key)
                if tx_report["status"] == True:
                    # If transation is scuccessfull update the has_voted in aadhaar database
                    try:
                        Aadhaar.objects.filter(email=request.user.email).update(
                            has_voted=True
                        )
                    except Exception as e:
                        print(colored(e, "red"))
                    messages.success(request, "vote submitted Successfully.")
                else:
                    # If transaction failed
                    messages.error(request, "couldn't transact vote")
            else:
                # If the public key is not matched with the registered public key in database
                messages.error(
                    request,
                    "Your private couldn't verify with the registered public key.",
                )
        else:
            # If transaction is made in different phase.
            # This scenerio only occurs if the voting phases are not handled well(i.e: if u don't check
            # the phase before you display the contestants list.)
            messages.error(request, "Can't vote Now. Phase Didn't match")

    # Get Request
    # Check Phase
    current_phase = contest.get_current_phase()
    if current_phase == "voting":
        # If phase is voting phase
        try:
            # Get the voter object to check if he has voted or not
            voter = Aadhaar.objects.get(email=request.user.email)
        except Exception as e:
            print(colored(e, "red"))
            messages.error(request, "email not in aadhaar database")
        if voter.has_voted == False:
            # If voter is not yet voted then return conestants list, current phase (helpful to check phase in templates)
            # and already_voted
            contestants_list = contest.get_contestants()
            context = {
                "contestants_list": contestants_list,  #
                "current_phase": current_phase,  # returns string()
                "already_voted": False,
            }
        else:
            # If voter has voted return already_voted to true and don't set contestants_list to None.
            context = {
                "current_phase": current_phase,
                "already_voted": True,
                "contestants_list": None,
            }
    else:
        # If it's not voting phase , return the current voting phase.
        # This should be handled in the jinja templates
        context = {
            "current_phase": current_phase,
            "contestants_list": None,
        }
    return render(request, "voting_area.html", context=context)


"""
Incase if we need to normalize and validate the email from the user input
if request.method == 'POST':
        form = YourForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                validate_email(email)
            except ValidationError:
                form.add_error('email', 'Please enter a valid email address.')
                return render(request, 'your_template.html', {'form': form})
            normalized_email = normalize_email(email)
            # ... rest of your code
"""
