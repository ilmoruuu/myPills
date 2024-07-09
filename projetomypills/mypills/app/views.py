from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the my pills index")

def login(request):
    return render(request, 'app/login.html')