from django.contrib import admin

from .models import DashboardMetric


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_spend', 'potential_savings', 'report_date')
