from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('ml/', include('ml.urls', namespace='ml')),
    path('optimizer/', include('optimizer.urls', namespace='optimizer')),
]
