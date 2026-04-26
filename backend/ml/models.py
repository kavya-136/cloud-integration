from django.conf import settings
from django.db import models


class PredictionModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions',
        null=True,
        blank=True,
    )
    input_data = models.JSONField(default=dict)
    prediction_result = models.JSONField(default=dict)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Prediction {self.id}'


class CloudDataset(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cloud_datasets',
    )
    cpu = models.FloatField()
    memory = models.FloatField()
    cost = models.FloatField()
    tag = models.CharField(max_length=100)
    cloud = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.cloud} - {self.tag}'


class AnomalyRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='anomaly_records',
    )
    input_data = models.JSONField(default=dict)
    anomaly_detected = models.BooleanField(default=False)
    anomaly_type = models.CharField(max_length=100, blank=True)
    severity = models.CharField(max_length=20, blank=True)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'AnomalyRecord {self.id} - {self.anomaly_type or "normal"}'
