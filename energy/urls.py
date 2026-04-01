import django.urls
from . import views

urlpatterns = [
    django.urls.path('data/', views.receive_data),
    django.urls.path('data/all/', views.get_data),
]
urlpatterns = [
    django.urls.path('', views.dashboard, name='dashboard'),
    django.urls.path('data/', views.receive_data),
    django.urls.path('data/all/', views.get_data),

    django.urls.path('device/on/', views.turn_on),
    django.urls.path('device/off/', views.turn_off),
    django.urls.path('device/status/', views.get_status),
]