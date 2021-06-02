
from django.urls import path
from maily.views import *


urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('login/report/', report, name='report'),
    path('login/report/delete/', delete, name='delete'),
    path('login/report/delete/confirm', confirm, name='confirm'),
    path('login/report/delete/result/', result, name='result'),
]
