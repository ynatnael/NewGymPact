from django.urls import path
from .views import home,signUp,success #,runWeeklyCheck# Import the views function

urlpatterns = [
    path('', home, name='home'),  # URL for the homepage
    path('signUp', signUp, name='signUp'),
    path('success', success, name='success'),
    #path("api/naty-says-run-weekly-check/", runWeeklyCheck, name="runWeeklycheck"),

]
