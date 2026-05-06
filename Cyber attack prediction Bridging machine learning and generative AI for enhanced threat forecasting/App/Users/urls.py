from django.urls import path
from Users.views import *

urlpatterns = [
    path('userhome/', userhome, name='userhome'),
    path('prediction/', prediction, name='prediction'),
    path('datavisulization/', datavisulization, name='datavisulization'),
    path('exsisting/', exsisting, name='exsisting'),
    path('proposed/', proposed, name='proposed'),
    path('history/', history, name='history'),
    path('analytics/', analytics, name='analytics'),
]