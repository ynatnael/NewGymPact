
from django.http import JsonResponse
import json
import os
from NewGymPact.mainApp.gymAPI import checkVisits
from NewGymPact.mainApp.models import UserList
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def getData(request):
        # API endpoint to manually trigger the gym visit check.
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

