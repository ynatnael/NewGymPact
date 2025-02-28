from django.urls import path
from . import views # Import the views function

urlpatterns = [
    path('', views.home, name='home'),  # URL for the homepage
    path('signUp', views.signUp, name='signUp'),
    path('success', views.success, name='success'),
    path('naty-says-run-weekly-check', views.runWeeklyCheck, name='runWeeklyCheck'),
    path('login', views.login, name='login'),
    path('settings', views.settings, name ='settings')

]
