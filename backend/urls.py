from django.contrib import admin
from django.urls import path, include
from energy.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('mobile_api.urls')),
    path('api/renewable/', include('renewable.urls')),
    path('', dashboard, name='dashboard'),
    path('api/energy/', include('energy.urls')),  
]