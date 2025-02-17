from django.urls import path
from .views import home,signUp,success# Import the view function

urlpatterns = [
    path('', home, name='home'),  # URL for the homepage
    path('signUp', signUp, name='signUp'),
    path('success', success, name='success'),

]
