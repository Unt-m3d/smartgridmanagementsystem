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
    path('api/', include('energy.urls')),  # API routes under /api/
    path('', TemplateView.as_view(template_name='index.html'), name='home'),  # Home page serves frontend
]

# Serve static files in development
if settings.DEBUG:
    # Convert WindowsPath to string for Django's static() function
    static_dirs = [str(d) for d in settings.STATICFILES_DIRS]
    urlpatterns += static('/static/', document_root=str(settings.STATIC_ROOT))
    urlpatterns += static('/frontend/', document_root=static_dirs[0])