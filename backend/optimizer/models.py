from django.conf import settings
from django.db import models


class Recommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True,
    )
    resource_name = models.CharField(max_length=255)
    current_cost = models.DecimalField(max_digits=10, decimal_places=2)
    optimized_cost = models.DecimalField(max_digits=10, decimal_places=2)
    savings_percent = models.DecimalField(max_digits=5, decimal_places=2)
    recommendation_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.resource_name} - {self.savings_percent}% savings'


class BudgetAlert(models.Model):
    ALERT_NORMAL = 'normal'
    ALERT_WARNING = 'warning'
    ALERT_CRITICAL = 'critical'
    ALERT_CHOICES = (
        (ALERT_NORMAL, 'Normal'),
        (ALERT_WARNING, 'Warning'),
        (ALERT_CRITICAL, 'Critical'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_alerts')
    threshold = models.DecimalField(max_digits=12, decimal_places=2)
    current_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    alert_status = models.CharField(max_length=20, choices=ALERT_CHOICES, default=ALERT_NORMAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user_id} budget {self.alert_status}'


class ShutdownSchedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shutdown_schedules')
    schedule_name = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f'{self.schedule_name} ({self.user_id})'


class Simulation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='simulations')
    input_params = models.JSONField(default=dict)
    simulated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    current_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Simulation {self.id}'


class CarbonFootprint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carbon_footprints')
    cpu = models.FloatField()
    memory = models.FloatField()
    carbon_grams = models.FloatField()
    region = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Carbon {self.user_id} {self.carbon_grams:.2f}g'


class SustainabilityScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sustainability_scores')
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    breakdown = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Sustainability {self.user_id}: {self.score:.1f}'


class RegionRecommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='region_recommendations')
    current_region = models.CharField(max_length=50)
    recommended_region = models.CharField(max_length=50)
    cost_difference = models.DecimalField(max_digits=12, decimal_places=2)
    savings_percent = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.current_region} -> {self.recommended_region}'


class KubernetesSimulation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kubernetes_simulations')
    pod_config = models.JSONField(default=dict)
    predicted_cost = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'K8s sim {self.id}'


class ChatbotInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chatbot_interactions')
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'ChatbotInteraction {self.id}'
