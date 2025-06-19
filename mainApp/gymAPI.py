import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

from anymail.message import AnymailMessage
from decouple import config, Csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
from django.core.mail import send_mail


# Email docs https://anymail.dev/en/v10.1/esps/brevo/
def send_email_notification(notificationEmail,email, username, goal, pastWeekMins, pastWeek, email_type):
    """Helper function to send emails with proper error handling"""

    templates = {
        'hit_goal': {
            'subject': "Congratulations On Hitting Your Gym Goals This Week",
            'partnerSub':f"Congratulate {username} On Hitting Their Gym Goals This Week",
            'template_id': 1
        },
        'exceeded_goal': {
            'subject': "Congratulations On Exceeding Your Gym Goals This Week",
            'partnerSub': f"Congratulate {username} On Exceeding Their Gym Goals This Week",
            'template_id': 2
        },
        'missed_goal': {
            'subject': "Unfortunately You Didn't Hit Your Gym Goals This Week",
            'partnerSub': f"Unfortunately {username} Didn't Hit Their Gym Goals This Week",
            'template_id': 3
        }
    }

    template_info = templates[email_type]

    try:
        #Email to gymgoer
        email = AnymailMessage(
            subject=template_info['subject'],
            from_email="Naty@gympact.fit",
            to=[email]
        )
        email.template_id = template_info['template_id']
        email.merge_data = {
            email: {
                "subject": template_info['subject'],
                "first_name": username,
                "goal": str(goal),
                "time": str(pastWeekMins),
                "visits": str(pastWeek)
            }
        }

        result = email.send()
        print(f"Email sent successfully to {notificationEmail}. Result: {result}")

        #Email to partner
        email = AnymailMessage(
            subject=template_info['partnerSub'],
            from_email="Naty@gympact.fit",
            to=[notificationEmail]
        )
        email.template_id = template_info['template_id']
        email.merge_data = {
            notificationEmail: {
                "subject": template_info['partnerSub'],
                "first_name": f"{username}'s friend",
                "goal": str(goal),
                "time": str(pastWeekMins),
                "visits": str(pastWeek)
            }
        }

        result = email.send()
        print(f"Email sent successfully to {notificationEmail}. Result: {result}")
        return True

    except Exception as e:
        print(f"Failed to send email to {notificationEmail}: {str(e)}")
        return False

def login(email, password):
    base_headers = {
        "accept": "application/json",
        "accept-encoding": "gzip",
        "connection": "Keep-Alive",
        "host": "thegymgroup.netpulse.com",
        "user-agent": "okhttp/3.12.3",
        "x-np-api-version": "1.5",
        "x-np-app-version": "9999",  # Updated to force latest API version
        "x-np-user-agent": "clientType=MOBILE_DEVICE; devicePlatform=ANDROID; deviceUid=; applicationName=The Gym Group; applicationVersion=5.0; applicationVersionCode=38"
    }

    global profile_headers
    profile_headers = base_headers.copy()

    # Prepare the data and calculate content length properly
    creds = {"username": email, "password": password}
    creds_encoded = urlencode(creds)

    base_headers["content-length"] = str(len(creds_encoded))
    base_headers["content-type"] = "application/x-www-form-urlencoded"

    response = requests.post("https://thegymgroup.netpulse.com/np/exerciser/login", data=creds, headers=base_headers)

    if response.status_code != 200:
        print(f"Login failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

    cookie = response.headers.get("Set-Cookie")
    if not cookie:
        print("No Set-Cookie header found in response")
        return False

    profile_headers["cookie"] = cookie

    global user_id
    try:
        user_id = response.json()["uuid"]
        print(f"Login successful. User ID: {user_id}")
        return True
    except KeyError:
        print("No UUID found in response")
        print(f"Response JSON: {response.json()}")
        return False


def get_url(url):  # could combine with next function
    print(f"Making request to: {url}")
    profile = requests.get(url, headers=profile_headers)

    if profile.status_code != 200:
        print(f"Request failed with status code: {profile.status_code}")
        print(f"Response: {profile.text}")
        return None

    return profile.json()


def getVisits(endDate):
    # Try both URL variations as there's inconsistency in the documentation
    urls_to_try = [
        f"https://thegymgroup.netpulse.com/np/exercisers/{user_id}/check-ins/history?endDate={endDate}",
        f"https://thegymgroup.netpulse.com/np/exerciser/{user_id}/check-ins/history?endDate={endDate}"
    ]

    for url in urls_to_try:
        print(f"Trying URL: {url}")
        result = get_url(url)
        if result is not None:
            return result

    print("All URL variations failed")
    return None


def checkVisits(username, email, pin, notificationEmail, goal):  # going to need to change this eventually

    # Get today's date and one week ago
    today = datetime.now()
    one_week_ago = today - timedelta(weeks=1)

    # Format the date in proper ISO format (no URL encoding needed)
    endDate = today.strftime("%Y-%m-%dT%H:%M:%S")

    print(f"Checking visits from {one_week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")

    # Login first
    if not login(email, pin):
        print("Login failed, cannot proceed")
        return []

    visits = getVisits(endDate)

    if not visits or "checkIns" not in visits:
        print("No visits data received")
        return []

    print(f"Retrieved {len(visits['checkIns'])} total check-ins")

    pastWeek = 0
    pastWeekMins = 0

    for i in visits["checkIns"]:
        checkin_date = datetime.fromisoformat(i['checkInDate'].replace('Z', '+00:00'))
        if checkin_date >= one_week_ago:
            pastWeek += 1
            pastWeekMins += int(i["duration"] / 60000)  # Convert milliseconds to minutes

    print(f"Visits in past week: {pastWeek}")
    print(f"Total time in past week: {pastWeekMins} minutes")

    #Convert goal to int
    goal = int(goal)


    if pastWeek == goal:
        print('You hit your target this week, Well Done')
        send_email_notification(notificationEmail,email, username, goal, pastWeekMins, pastWeek, 'hit_goal')
    elif pastWeek > goal:
        print('You exceeded your target this week, Well Done')
        send_email_notification(notificationEmail,email, username, goal, pastWeekMins, pastWeek, 'exceeded_goal')
    else:
        print('You missed your target this week, Try harder next week')
        send_email_notification(notificationEmail,email, username, goal, pastWeekMins, pastWeek, 'missed_goal')

        print(f"Total time spent in the gym this week: {pastWeekMins} minutes")
        return visits['checkIns']

# Example usage (uncomment to test):
# if __name__ == "__main__":
#     checkVisits("YourName", "your@email.com", "your_pin", "notification@email.com", 3)