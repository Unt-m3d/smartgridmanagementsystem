from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('daily-trends/', views.get_daily_trends, name='daily-trends'),
    path('hourly-trends/', views.get_hourly_trends, name='hourly-trends'),
    path('calculate-trends/', views.calculate_trends, name='calculate-trends'),
    path('predict/', views.predict_energy, name='predict-energy'),
    path('statistics/', views.get_statistics, name='statistics'),
]