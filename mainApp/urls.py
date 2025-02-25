from django.urls import path
from . import views # Import the views function

urlpatterns = [
    path('', views.home, name='home'),  # URL for the homepage
    path('signUp', views.signUp, name='signUp'),
    path('success', views.success, name='success'),
    #path("api/naty-says-run-weekly-check/", runWeeklyCheck, name="runWeeklycheck"),
    path('naty-says-run-weekly-check', views.runWeeklyCheck, name='runWeeklyCheck'),

]
