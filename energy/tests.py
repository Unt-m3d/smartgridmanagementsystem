from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from rest_framework import status
from .models import EnergyData, DeviceStatus
import json

class EnergyDataModelTest(TestCase):
    """Test EnergyData model"""
    
    def setUp(self):
        self.energy = EnergyData.objects.create(
            voltage=230,
            current=2.5,
            power=575
        )

    def test_energy_data_creation(self):
        """Test energy data creation"""
        self.assertEqual(self.energy.power, 575)
        self.assertEqual(self.energy.voltage, 230)
        self.assertEqual(self.energy.current, 2.5)

    def test_energy_string_representation(self):
        """Test string representation"""
        self.assertIn("575", str(self.energy))

    def test_negative_power_rejected(self):
        """Test that negative power is rejected"""
        invalid = EnergyData(voltage=230, current=-2.5, power=-575)
        with self.assertRaises(ValidationError):
            invalid.full_clean()

    def test_negative_voltage_rejected(self):
        """Test that negative voltage is rejected"""
        invalid = EnergyData(voltage=-230, current=2.5, power=575)
        with self.assertRaises(ValidationError):
            invalid.full_clean()

    def test_zero_values_allowed(self):
        """Test that zero values are allowed"""
        valid = EnergyData(voltage=0, current=0, power=0)
        try:
            valid.full_clean()
        except ValidationError:
            self.fail("Zero values should be allowed")


class DeviceStatusModelTest(TestCase):
    """Test DeviceStatus model"""
    
    def setUp(self):
        self.device = DeviceStatus.objects.create(
            device_id='test_device',
            status='on'
        )

    def test_device_creation(self):
        """Test device creation"""
        self.assertEqual(self.device.status, 'on')

    def test_device_status_update(self):
        """Test device status update"""
        self.device.status = 'off'
        self.device.save()
        self.device.refresh_from_db()
        self.assertEqual(self.device.status, 'off')


class EnergyAPITest(TestCase):
    """Test Energy API endpoints"""
    
    def setUp(self):
        self.client = Client()
        EnergyData.objects.create(voltage=230, current=2.5, power=575)

    def test_post_energy_data(self):
        """Test POST /api/data/"""
        data = {'voltage': 240, 'current': 3.0, 'power': 720}
        response = self.client.post(
            '/api/data/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_get_all_data(self):
        """Test GET /api/data/all/"""
        response = self.client.get('/api/data/all/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_data_with_limit(self):
        """Test pagination"""
        for i in range(10):
            EnergyData.objects.create(
                voltage=230+i, current=2.5+i, power=575+(i*10)
            )
        response = self.client.get('/api/data/all/?limit=5')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.json()), 5)

    def test_turn_on(self):
        """Test POST /api/device/on/"""
        response = self.client.post('/api/device/on/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['on'])

    def test_turn_off(self):
        """Test POST /api/device/off/"""
        response = self.client.post('/api/device/off/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['on'])

    def test_get_status(self):
        """Test GET /api/device/status/"""
        response = self.client.get('/api/device/status/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('on', response.json())

    def test_device_persistence(self):
        """Test device status persists"""
        self.client.post('/api/device/off/')
        response = self.client.get('/api/device/status/')
        self.assertFalse(response.json()['on'])