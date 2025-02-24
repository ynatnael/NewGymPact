import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
import yagmail # getting rid of this
from anymail.message import AnymailMessage
from decouple import config, Csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
from django.core.mail import send_mail

#Email docs https://anymail.dev/en/v10.1/esps/brevo/



def login(username,password):
    base_headers = {
        "accept": "application/json",
        "accept-encoding": "gzip",
        "connection": "Keep-Alive",
        "host": "thegymgroup.netpulse.com",
        "user-agent": "okhttp/3.12.3",
        "x-np-api-version": "1.5",
        "x-np-app-version": "6.0.1",
        "x-np-user-agent": "clientType=MOBILE_DEVICE; devicePlatform=ANDROID; deviceUid=; applicationName=The Gym Group; applicationVersion=5.0; applicationVersionCode=38"}


    global profile_headers
    profile_headers = base_headers.copy()
    base_headers["content-length"] = "56"
    base_headers["content-type"] = "application/x-www-form-urlencoded"
    creds = {"username": username, "password": password}

    response = requests.post("https://thegymgroup.netpulse.com/np/exerciser/login", data=creds, headers=base_headers)
    cookie = response.headers["Set-Cookie"]
    profile_headers["cookie"] = cookie
    global user_id
    user_id = response.json()["uuid"]

def get_url(url): # could combine with next function
    profile = (requests.get(url,headers=profile_headers))
    return profile.json()

def getVisits(endDate):
    return get_url(f"https://thegymgroup.netpulse.com/np/exercisers/{user_id}/check-ins/history?endDate={endDate}")

def checkVisits(username,pin,notificationEmail,goal): #going to need to change this eventually

    # Get today's date and one week ago
    today = datetime.now()
    one_week_ago = today - timedelta(weeks=1)

    # Format the dates in the required format (e.g., "YYYY-MM-DDTHH%3AMM%3ASS")
    date_format = "%Y-%m-%dT%H%%3A%M%%3A%S"  # %3A represents ':' for URL encoding
    #startDate = one_week_ago.strftime(date_format)
    endDate = today.strftime(date_format)

    login(username,pin)
    visits = getVisits(endDate)
    print(visits)

    mins=0

    gmail_user = config('GMAIL_USER')
    gmail_password = config('GMAIL_PASSWORD')

    if not gmail_user and gmail_password:
        raise ValueError("GMAIL_USER or GMAIL_PASSWORD is not set in environment variables")

    # Pass credentials explicitly
    yag = yagmail.SMTP(gmail_user, gmail_password)


    pastWeek = 0
    pastWeekMins = 0
    for i in visits["checkIns"]:
        if datetime.fromisoformat(i['checkInDate']) >= one_week_ago:
            pastWeek+=1
            pastWeekMins+=int(i["duration"] / 60000)

    if pastWeek == goal:
        print('You hit your target this week, Well Done')
        email = AnymailMessage(
            subject="Congratulations On Hitting Your Gym Goals This Week",
            from_email="Naty@gympact.fit",
            to=[notificationEmail]
        )
        email.template_id = 1
        # Add parameters
        email.merge_data = {
            notificationEmail: {
                "first_name": 'Naty',     #BS tbf
                "goal": str(goal),
                "time":str(pastWeekMins),
                "visits":str(pastWeek) #number of visits that week
            }
        }
        # Send email
        email.send()

    elif pastWeek > goal:
        print('You exceeded your target this week, Well Done')
        email = AnymailMessage(
            subject="Congratulations On Exceeding Your Gym Goals This Week",
            from_email="Naty@gympact.fit",
            to=[notificationEmail]
        )
        email.template_id = 2
        # Add parameters
        email.merge_data = {
            notificationEmail: {
                "first_name": 'Naty',
                "goal": str(goal),
                "time": str(pastWeekMins),
                "visits": str(pastWeek)  # number of visits that week
            }
        }
        # Send email
        email.send()
    else:
        print('You missed your target this week, Try harder next week')
        email = AnymailMessage(
            subject="Unfortunately You Didn't Hit Your Gym Goals This Week",
            from_email="Naty@gympact.fit",
            to=[notificationEmail]
        )
        email.template_id = 3
        # Add parameters
        email.merge_data = {
            notificationEmail: {
                "first_name": 'Naty',
                "goal": str(goal),
                "time": str(pastWeekMins),
                "visits": str(pastWeek)  # number of visits that week
            }
        }
        # Send email
        email.send()
    print(f"Total time spent in the gym this week {pastWeekMins} minutes")
    return visits['checkIns']

#print("You have spent", str(round(mins / 60)), "hours in the gym since ", visits["checkIns"][len(visits["checkIns"]-1)]["checkInDate"])
