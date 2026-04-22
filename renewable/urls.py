from django.urls import path
from . import views

app_name = 'renewable'

urlpatterns = [
    path('add-source/', views.add_renewable_source, name='add-source'),
    path('sources/', views.get_renewable_sources, name='sources'),
    path('record-data/', views.record_renewable_data, name='record-data'),
    path('generation/', views.get_renewable_generation, name='generation'),
    path('carbon-savings/', views.get_carbon_savings, name='carbon-savings'),
    path('record-carbon/', views.record_carbon_savings, name='record-carbon'),
    path('renewable-percentage/', views.get_renewable_percentage, name='renewable-percentage'),
]