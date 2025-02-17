from .models import UserList
from datetime import datetime, timedelta
from .gymAPI import checkVisits #Add anything else that comes from my script
from django.shortcuts import render, HttpResponse, redirect


# Create your views here.
def home(request):
    return render(request, "home/home.html")

def signUp(request):
    if request.method == "POST":
        username = request.POST.get("email")
        pin = request.POST.get("pin")
        notificationEmail = request.POST.get("notificationEmail")
        goal = int(request.POST.get("goal"))

        # Save user data if new
        try:
            user = UserList.objects.get(username=username)
            print(f"Existing user found: {user}")
        except UserList.DoesNotExist:
            user = UserList.objects.create(
                username=username,
                pin=pin,
                notificationEmail=notificationEmail,
                goal=goal,
            )
            print(f"New user created: {user}")

        # Perform the gym check
        visits = checkVisits(username, pin, notificationEmail,goal)
        for visit in visits:
            visit['duration'] = round(visit['duration'] / 60000, 2)  # Convert duration to minutes
            visit['checkInDate'] = datetime.fromisoformat(visit['checkInDate'])
            visit['date'] = visit['checkInDate'].strftime('%Y-%m-%d')
            visit['time'] = visit['checkInDate'].strftime('%H:%M:%S')
            del visit['checkInDate']  # Remove original checkInDate
            del visit['gymLocationAddress']  # Remove address field

        #visit count

        return render(request, "home/success.html", {
        'visits': visits})
    return render(request, "signUp.html")

def success(request):
    return render(request, "home/success.html")