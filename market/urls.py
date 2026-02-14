# market/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La vue pour la page d'accueil s'appelle 'accueil' dans votre views.py
    path('', views.accueil, name='home'), 

    path('register/', views.vendor_register, name='vendor_register'),
    path('login/', views.vendor_login, name='vendor_login'),
    path('logout/', views.vendor_logout, name='vendor_logout'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('premium/', views.premium_page, name='premium'),

    #path('vendor/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('vendor/<int:pk>/', views.vendor_detail, name='vendor_detail'),
]
