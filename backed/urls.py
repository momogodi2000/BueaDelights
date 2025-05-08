from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='homepage'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),



    path('adminpanel/', views.adminpanel, name='adminpanel'),
    path('delivery/', views.delivery, name='delivery'),
    path('client/', views.client, name='client'),


]