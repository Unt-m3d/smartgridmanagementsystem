from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('data/', views.receive_data, name='receive_data'),
    path('data/all/', views.get_data, name='get_data'),
    path('device/on/', views.turn_on, name='turn_on'),
    path('device/off/', views.turn_off, name='turn_off'),
    path('device/status/', views.get_status, name='get_status'),
]