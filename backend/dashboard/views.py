from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html', {'user': request.user})
