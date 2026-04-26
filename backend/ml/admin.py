from django.contrib import admin

from .models import PredictionModel


@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
