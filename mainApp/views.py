from datetime import datetime, timedelta
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
import json
import os
from .gymAPI import checkVisits
from .models import UserList
from rest_framework.response import Response
from rest_framework.decorators import api_view




# Create your views here.


def home(request):
    return render(request, "home/home.html")

def success(request):
    return render(request, "home/success.html")

def signUp(request):
    if request.method == "POST":
        username = request.POST.get("email")
        pin = request.POST.get("pin")
        notificationEmail = request.POST.get("notificationEmail")
        goal = int(request.POST.get("goal"))

        # Check if user already exists
        try:
            user = UserList.objects.get(username=username)
            print(f"Existing user found: {user}")
        except UserList.DoesNotExist:
            # Create a new user if it doesn't exist
            user = UserList.objects.create(
                username=username,
                pin=pin,
                notificationEmail=notificationEmail,
                goal=goal,
            )
            print(f"New user created: {user}")

        # Perform the gym check regardless of whether user is new or existing
        try:
            visits = checkVisits(username, pin, notificationEmail, goal)
        except ValueError as e:
            return render(request, "signUp.html", {"error_message": str(e)})
        except Exception as e:  # Catch other unexpected errors
            return render(request, "signUp.html", {"error_message": f"Unexpected error: {str(e)}"})


        for visit in visits:
            visit['duration'] = round(visit['duration'] / 60000, 2)  # Convert duration to minutes
            visit['checkInDate'] = datetime.fromisoformat(visit['checkInDate'])
            visit['date'] = visit['checkInDate'].strftime('%Y-%m-%d')
            visit['time'] = visit['checkInDate'].strftime('%H:%M:%S')
            del visit['checkInDate']  # Remove original checkInDate
            del visit['gymLocationAddress']  # Remove address field

        return render(request, "home/success.html", {
            'visits': visits
        })

    return render(request, "signUp.html")


@api_view(['GET'])
def runWeeklyCheck(request):
    #API endpoint to manually trigger the gym visit check.
    print(f"Valid method: {request.method}")  # Debugging
    if request.method == "POST":
        print(f"Valid method: {request.method}")  # Debugging
        secret_key = request.headers.get("Authorization")  # Simple security check
        expected_key = os.getenv("CRON_SECRET_KEY")

        print(f"Received secret key: {secret_key}")  # Debugging
        print(f"Expected secret key: {expected_key}")  # Debugging

        if secret_key != expected_key:
            print("Unauthorized: Invalid secret key")  # Debugging
            return JsonResponse({"error": "Unauthorized"}, status=403)

        users = UserList.objects.all()
        results = []

        for user in users:
            try:
                visits = checkVisits(user.username, user.pin, user.notificationEmail, int(user.goal))
                total_visits = len(visits)
                status = f"{user.username} has {'met' if total_visits >= user.goal else 'NOT met'} their goal"
                results.append({"user": user.username, "status": status})
            except Exception as e:
                results.append({"user": user.username, "error": str(e)})

        return JsonResponse({"message": "Cron task executed", "results": results}, status=200)

    return Response({"message": "Scheduler Failed!"}, status=400)

