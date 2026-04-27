from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import RenewableSource, RenewableData, CarbonSavings
import json

class RenewableSourceAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.add_source_url = reverse('add-source')
        self.get_sources_url = reverse('sources')
        
    def test_add_renewable_source_success(self):
        """Test adding a valid renewable source"""
        data = {
            'name': 'Rooftop Solar',
            'source_type': 'SOLAR',  # Use uppercase
            'capacity': 10,
            'location': 'Building A',
            'is_active': True
        }
        response = self.client.post(self.add_source_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
    def test_add_renewable_source_invalid_type(self):
        """Test adding source with invalid source_type"""
        data = {
            'name': 'Rooftop Solar',
            'source_type': 'solar',  # lowercase - should fail
            'capacity': 10,
            'location': 'Building A',
            'is_active': True
        }
        response = self.client.post(self.add_source_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_add_wind_source(self):
        """Test adding a wind turbine"""
        data = {
            'name': 'Wind Turbine',
            'source_type': 'WIND',
            'capacity': 50,
            'location': 'Hill Area',
            'is_active': True
        }
        response = self.client.post(self.add_source_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_get_renewable_sources(self):
        """Test retrieving renewable sources"""
        # Create a source
        RenewableSource.objects.create(
            name='Solar Panel',
            source_type='SOLAR',
            capacity=10,
            location='Building A',
            is_active=True
        )
        
        response = self.client.get(self.get_sources_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)


class RenewableDataAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.record_data_url = reverse('record-data')
        self.get_generation_url = reverse('generation')
        
        # Create a renewable source first
        self.source = RenewableSource.objects.create(
            name='Solar Panel',
            source_type='SOLAR',
            capacity=10,
            location='Building A',
            is_active=True
        )
    
    def test_record_renewable_data_success(self):
        """Test recording valid renewable data"""
        data = {
            'source': self.source.id,
            'power_generated': 5000,
            'efficiency': 85
        }
        response = self.client.post(self.record_data_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
    def test_record_renewable_data_missing_fields(self):
        """Test recording data with missing required fields"""
        data = {
            'source': self.source.id,
            'power_generated': None,  # Missing
            'efficiency': None  # Missing
        }
        response = self.client.post(self.record_data_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_get_renewable_generation(self):
        """Test retrieving renewable generation data"""
        # Create data
        RenewableData.objects.create(
            source=self.source,
            power_generated=5000,
            efficiency=85
        )
        
        response = self.client.get(self.get_generation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)


class CarbonSavingsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.record_carbon_url = reverse('record-carbon')
        self.get_carbon_url = reverse('carbon-savings')
        
    def test_record_carbon_savings_success(self):
        """Test recording carbon savings"""
        data = {
            'date': date.today().isoformat(),
            'renewable_energy_kwh': 100,
            'carbon_saved_kg': 50,
            'cost_saved': 150
        }
        response = self.client.post(self.record_carbon_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
    def test_get_carbon_savings(self):
        """Test retrieving carbon savings"""
        # Create carbon savings record
        CarbonSavings.objects.create(
            date=date.today(),
            renewable_energy_kwh=100,
            carbon_saved_kg=50,
            cost_saved=150
        )
        
        response = self.client.get(self.get_carbon_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        
    def test_get_carbon_savings_with_days_filter(self):
        """Test retrieving carbon savings with days filter"""
        response = self.client.get(f'{self.get_carbon_url}?days=7')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class RenewablePercentageAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.renewable_percentage_url = reverse('renewable-percentage')
        
    def test_get_renewable_percentage(self):
        """Test getting renewable energy percentage"""
        # Create carbon savings record
        CarbonSavings.objects.create(
            date=date.today(),
            renewable_energy_kwh=100,
            carbon_saved_kg=50,
            cost_saved=150
        )
        
        response = self.client.get(self.renewable_percentage_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('renewable_percentage', response.data)
        
    def test_get_renewable_percentage_with_days_filter(self):
        """Test renewable percentage with custom days filter"""
        response = self.client.get(f'{self.renewable_percentage_url}?days=30')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])