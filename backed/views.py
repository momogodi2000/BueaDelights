from django.shortcuts import render


def home(request):
    return render(request, 'LandingPage/homepage.html')

def login(request):
    return render(request, 'Authentication/login.html')
