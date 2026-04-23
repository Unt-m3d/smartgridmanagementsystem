"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('energy.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/renewable/', include('renewable.urls')),
    
    # ✅ ADDED: Route for mobile.html
    path('mobile/', TemplateView.as_view(template_name='mobile.html'), name='mobile'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static('/frontend/', document_root=os.path.join(settings.BASE_DIR, 'frontend'))
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'staticfiles'))