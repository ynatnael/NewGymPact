from datetime import datetime, timedelta
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
import json
import os
from .gymAPI import checkVisits
from .models import UserList
from rest_framework.response import Response
from rest_framework.decorators import api_view
from decouple import config, Csv
# mainApp/views.py
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from .models import CustomUser
from django.contrib.auth import get_user_model




# Create your views here.


def home(request):
    return render(request, "home/home.html")

def success(request):
    return render(request, "home/success.html")

#Very lousy way to run this - Basically the signup function without notification email, sends more API requests to thegym, code is messy, should be using functions and password should be hashed

def login(request):
    print(f"Login view called with method: {request.method}")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(f"Attempting login for email: {email}")

        user = authenticate(request, username=email, password=password)
        print(f"Authentication result: {user}")

        if user is not None:
            auth_login(request, user)
            print(f"User {user.email} logged in successfully - redirecting to dashboard")
            return redirect('dashboard')
        else:
            print("Authentication failed")
            messages.error(request, "Invalid email or password")
            return render(request, "login.html")

    print("Rendering login template for GET request")
    return render(request, "login.html")


def signUp(request):
    print(f"SignUp view called with method: {request.method}")
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        pin = request.POST.get("pin")
        notificationEmail = request.POST.get("notificationEmail")
        goal = int(request.POST.get("goal", 3))

        print(f"Signup attempt for email: {email}, username: {username}")

        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            print("User already exists")
            messages.error(request, "User with this email already exists")
            return render(request, "signup.html")

        try:
            # Create new user - Remove notificationEmail temporarily if field doesn't exist
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=pin,  # This should be the password
                pin=pin,
                goal=goal,
                # notificationEmail=notificationEmail  # Add this back after adding the field
            )
            print(f"New user created: {user}")

            # Auto-login the user after signup
            user = authenticate(request, username=email, password=pin)  # Use email as username
            print(f"Auto-login authentication result: {user}")

            if user:
                auth_login(request, user)
                print("User logged in successfully - redirecting to dashboard")
                messages.success(request, "Account created successfully!")
                return redirect('dashboard')
            else:
                print("Auto-login failed")
                messages.error(request, "Account created but login failed. Please try logging in manually.")
                return redirect('login')

        except Exception as e:
            print(f"Error creating user: {str(e)}")
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, "signup.html")

    print("Rendering signup template for GET request")
    return render(request, "signup.html")

@login_required
def dashboard(request):
    """Protected view that requires authentication"""
    try:
        # Use the logged-in user's data
        visits = checkVisits(
            request.user.username,
            request.user.email,
            request.user.pin,
            request.user.notificationEmail,
            request.user.goal
        )

        # Process visits data
        for visit in visits:
            visit['duration'] = round(visit['duration'] / 60000, 2)
            visit['checkInDate'] = datetime.fromisoformat(visit['checkInDate'])
            visit['date'] = visit['checkInDate'].strftime('%Y-%m-%d')
            visit['time'] = visit['checkInDate'].strftime('%H:%M:%S')
            del visit['checkInDate']
            del visit['gymLocationAddress']

        return render(request, "dashboard.html", {
            'visits': visits,
            'user': request.user
        })

    except Exception as e:
        print(f"Error retrieving gym data: {str(e)}")
        messages.error(request, f"Error retrieving gym data: {str(e)}")
        return render(request, "dashboard.html", {
            'visits': [],
            'user': request.user
        })


@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')

@api_view(['POST'])
def runWeeklyCheck(request):
    #API endpoint to manually trigger the gym visit check.
    if request.method == "POST":
        #logging.info("POST Request received successfully")
        secret_key = request.headers.get("Authorization")  # Simple security check
        expected_key = config("WEEKLY_CHECK_SECRET_KEY", default="zd6wLxa9bjJeDnI5")

        if secret_key != expected_key:
            #logging.error("Key's are not equal or not present")
            return JsonResponse({"error": "Unauthorized"}, status=403)

        User = get_user_model()  # This gets your CustomUser model
        users = User.objects.all()
        results = []

        for user in users:
            try:
                visits = checkVisits(user.username,user.email, user.pin, user.notificationEmail, int(user.goal))
                total_visits = len(visits)
                status = f"{user.username} has {'met' if total_visits >= user.goal else 'NOT met'} their goal"
                results.append({"user": user.username, "status": status})
                #logging.info(f'Successfully ran check for {user}')
            except Exception as e:
                results.append({"user": user.username, "error": str(e)})
                #logging.error(f'Run failed for {user}')

        return JsonResponse({"message": "Task executed", "results": results}, status=200)

    return Response({"message": "Scheduler Failed!"}, status=400)


@login_required
def settings(request):
    if request.method == "POST":
        notificationEmail = request.POST.get("notificationEmail")
        goal = int(request.POST.get("goal"))

        try:
            # Use the logged-in user directly
            user = request.user
            print(f"Updating settings for user: {user.email}")

            # Update the user's settings
            user.notificationEmail = notificationEmail
            user.goal = goal
            user.save()

            print("Updated settings successfully")
            messages.success(request, "Settings updated successfully!")
            return render(request, "settings.html", {
                "success_message": "Update Successful",
                "user": user
            })

        except Exception as e:
            print(f"Error updating settings: {str(e)}")
            messages.error(request, f"Error updating settings: {str(e)}")
            return render(request, "settings.html", {
                "error_message": "Failed to update settings",
                "user": request.user
            })

    # For GET requests, pass the current user's data to pre-populate the form
    return render(request, "settings.html", {"user": request.user})
