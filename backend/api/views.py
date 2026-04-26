from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def predict_api(request):
    cpu = float(request.GET.get('cpu', 10))
    memory = float(request.GET.get('memory', 20))

    return JsonResponse({
        "cpu": cpu,
        "memory": memory,
        "status": "API working"
    })