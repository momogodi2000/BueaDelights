from django.urls import path
from . import views

app_name = 'backed'

urlpatterns = [
    path('', views.home, name='homepage'),

]