from django.urls import path
from . import views

urlpatterns = [

    path('', views.user_login, name='login'),

    path('dashboard/', views.home, name='home'),

    path('rent/', views.rent, name='rent'),

    path('maintenance/', views.maintenance, name='maintenance'),

    path('complaints/', views.complaints, name='complaints'),

    
    path('complaint_list/', views.complaint_list, name='complaint_list'),

    path('history/', views.history, name='history'),

    path('profile/', views.profile, name='profile'),

    path("edit-profile/", views.edit_profile, name="edit_profile"),

    path("change-password/", views.change_password, name="change_password"),

    path("download/<int:payment_id>/", views.download_receipt, name="download_receipt"),
    
    path('logout/', views.user_logout, name='logout'),
    
    path("register/", views.register, name="register"),

]