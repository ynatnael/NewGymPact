from django.core.management.base import BaseCommand
from ...gymAPI import checkVisits
from ...models import UserList


class Command(BaseCommand):
    help = 'Every week this will run the gym check'

    def handle(self, *args, **kwargs):
        users = UserList.objects.all()
        self.stdout.write("Running my custom command...")
        for user in users:
            try:
                checkVisits(user.username,user.pin, user.notificationEmail, int(user.goal))
                self.stdout.write(self.style.SUCCESS(f"Checked visits for {user.username}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error checking visits for {user.username}: {str(e)}"))

#path to python
#/Users/natnaeltekeste/PycharmProjects/pythonProject2/venv/bin/python
#/Users/natnaeltekeste/PycharmProjects/pythonProject2/gympact/manage.py

#This will schedule it for 3am every monday , Minute,Hour,.,.,Day of the week, python interpreter, command file
#00 03 * * 1 /Users/natnaeltekeste/PycharmProjects/pythonProject2/venv/bin/python /Users/natnaeltekeste/PycharmProjects/pythonProject2/gympact/manage.py weeklyCommand>> /Users/natnaeltekeste/PycharmProjects/pythonProject2/gympact/cron.log 2>&1
