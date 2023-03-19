from django.shortcuts import render, redirect
from accounts.forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def register(request):
    form = CustomUserCreationForm()
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("login")
        else:
            messages.error(request, "confirmation password didn't match")
    return render(request, "register.html", {"form": form})


# def login(request):
#     if request.method == 'POST':
#         print("call to login via post request")
#         form = CustomUserLoginForm(request.POST)
#         if form.is_valid():
#             print("form is valid")
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             print(email, password)
#             user = authenticate(request, email=email, password=password)
#             print(user)
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 messages.error(request, 'Invalid email or password.')
#     else:
#         form = CustomUserLoginForm()
#     return render(request, 'login.html', {'form': form})


# def logout(request):
#     logout(request)
#     redirect('login')
