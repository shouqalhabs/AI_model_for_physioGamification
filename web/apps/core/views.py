from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect

def main_login(request):
    return render(request, 'core/main_login.html')
