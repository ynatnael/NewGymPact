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




# Create your views here.


def home(request):
    return render(request, "home/home.html")

def success(request):
    return render(request, "home/success.html")

def signUp(request):


    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
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
                email=email,
                pin=pin,
                notificationEmail=notificationEmail,
                goal=goal,
            )
            print(f"New user created: {user}")


        # Perform the gym check regardless of whether user is new or existing
        try:
            visits = checkVisits(email, pin, notificationEmail, goal)
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


@api_view(['POST'])
def runWeeklyCheck(request):
    #API endpoint to manually trigger the gym visit check.
    if request.method == "POST":
        #logging.info("POST Request received successfully")
        secret_key = request.headers.get("Authorization")  # Simple security check
        expected_key = config("WEEKLY_CHECK_SECRET_KEY")

        if secret_key != expected_key:
            #logging.error("Key's are not equal or not present")
            return JsonResponse({"error": "Unauthorized"}, status=403)

        users = UserList.objects.all()
        results = []

        for user in users:
            try:
                visits = checkVisits(user.email, user.pin, user.notificationEmail, int(user.goal))
                total_visits = len(visits)
                status = f"{user.username} has {'met' if total_visits >= user.goal else 'NOT met'} their goal"
                results.append({"user": user.username, "status": status})
                #logging.info(f'Successfully ran check for {user}')
            except Exception as e:
                results.append({"user": user.username, "error": str(e)})
                #logging.error(f'Run failed for {user}')

        return JsonResponse({"message": "Task executed", "results": results}, status=200)

    return Response({"message": "Scheduler Failed!"}, status=400)

