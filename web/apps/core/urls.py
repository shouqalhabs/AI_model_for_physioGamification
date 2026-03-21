from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_login, name= "main_login"),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('gamer-login/', views.gamer_login, name='gamer_login'),
]
 