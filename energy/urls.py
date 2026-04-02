import django.urls
from . import views

urlpatterns = [
    django.urls.path('', views.dashboard, name='dashboard'),
    django.urls.path('api/data/', views.receive_data),
    django.urls.path('api/data/all/', views.get_data),

    django.urls.path('api/device/on/', views.turn_on),
    django.urls.path('api/device/off/', views.turn_off),
    django.urls.path('api/device/status/', views.get_status),
]