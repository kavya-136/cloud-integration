from django.conf import settings
from django.db import models


class DashboardMetric(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_metrics',
        null=True,
        blank=True,
    )
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    potential_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    report_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Metrics {self.report_date}'
