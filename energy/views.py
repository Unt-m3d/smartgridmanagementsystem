from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import EnergyData
from .serializers import EnergyDataSerializer
device_status = {"on": True}

@api_view(['POST'])
def receive_data(request):
    serializer = EnergyDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Data saved"})
    return Response(serializer.errors)

@api_view(['GET'])
def get_data(request):
    data = EnergyData.objects.all()
    serializer = EnergyDataSerializer(data, many=True)
    return Response(serializer.data)
@api_view(['POST'])
def turn_on(request):
    device_status["on"] = True
    return Response({"status": "Device ON"})

@api_view(['POST'])
def turn_off(request):
    device_status["on"] = False
    return Response({"status": "Device OFF"})

@api_view(['GET'])
def get_status(request):
    return Response(device_status)
from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')    