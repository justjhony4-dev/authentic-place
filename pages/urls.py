from django.urls import path
from . import views

urlpatterns = [
    path('a-propos/', views.about, name='about'),
    path('conditions/', views.terms, name='terms'),
    path('confidentialite/', views.privacy, name='privacy'),
    path('contact/', views.contact, name='contact'),
]
