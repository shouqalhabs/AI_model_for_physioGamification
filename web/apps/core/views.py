from django.shortcuts import render

def main_login(request):
    return render(request, 'core/main_login.html')


def doctor_login(request):
    return render(request, 'core/doctor_login.html')


def gamer_login(request):
    return render(request, 'core/gamer_login.html')
