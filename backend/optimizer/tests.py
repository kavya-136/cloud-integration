import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser

from .models import (
    BudgetAlert,
    CarbonFootprint,
    ChatbotInteraction,
    KubernetesSimulation,
    Recommendation,
    RegionRecommendation,
    ShutdownSchedule,
    Simulation,
    SustainabilityScore,
)


class OptimizerTests(TestCase):
    def test_recommendations_requires_authentication(self):
        response = self.client.post(reverse('optimizer:recommendations'), data={'cpu': 10, 'memory': 10})
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('optimizer:recommendations')}")

    def test_recommendations_endpoint_for_authenticated_user(self):
        user = CustomUser.objects.create_user(username='optuser', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.post(
            reverse('optimizer:recommendations'),
            data={'cpu': 20, 'memory': 25, 'current_cost': 100},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertGreaterEqual(len(payload['data']['recommendations']), 1)
        self.assertIn('type', payload['data']['recommendations'][0])
        self.assertEqual(Recommendation.objects.count(), len(payload['data']['recommendations']))

    def test_recommendations_invalid_input(self):
        user = CustomUser.objects.create_user(username='optuser2', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.post(reverse('optimizer:recommendations'), data={'cpu': 'invalid', 'memory': 25})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_budget_set_and_status(self):
        user = CustomUser.objects.create_user(username='budgetuser', password='StrongPass1!')
        self.client.force_login(user)

        set_response = self.client.post(
            reverse('optimizer:budget_set'),
            data=json.dumps({'threshold': 100}),
            content_type='application/json',
        )
        self.assertEqual(set_response.status_code, 200)
        self.assertEqual(BudgetAlert.objects.count(), 1)
        self.assertIn('data', set_response.json())

        status_response = self.client.get(f"{reverse('optimizer:budget_status')}?current_cost=85")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()['data']['budget']['alert_status'], BudgetAlert.ALERT_WARNING)

        check_response = self.client.post(
            reverse('optimizer:budget_alert_check'),
            data=json.dumps({'current_cost': 120}),
            content_type='application/json',
        )
        self.assertEqual(check_response.status_code, 200)
        self.assertEqual(check_response.json()['data']['alert']['status'], BudgetAlert.ALERT_CRITICAL)

    def test_scheduler_set_list_and_toggle(self):
        user = CustomUser.objects.create_user(username='scheduleuser', password='StrongPass1!')
        self.client.force_login(user)
        schedule_time = (timezone.now() + timedelta(hours=2)).isoformat()

        set_response = self.client.post(
            reverse('optimizer:scheduler_set'),
            data=json.dumps({'schedule_name': 'night-shutdown', 'scheduled_time': schedule_time}),
            content_type='application/json',
        )
        self.assertEqual(set_response.status_code, 200)
        schedule_id = set_response.json()['data']['schedule']['id']
        self.assertEqual(ShutdownSchedule.objects.count(), 1)

        list_response = self.client.get(reverse('optimizer:scheduler_list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()['data']['schedules']), 1)
        self.assertIsNotNone(list_response.json()['data']['next_shutdown_time'])

        toggle_response = self.client.put(reverse('optimizer:scheduler_toggle', args=[schedule_id]))
        self.assertEqual(toggle_response.status_code, 200)
        self.assertFalse(toggle_response.json()['data']['schedule']['is_active'])

    def test_simulator_endpoint(self):
        user = CustomUser.objects.create_user(username='simuser', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.post(
            reverse('optimizer:simulator'),
            data=json.dumps({'current_cpu': 80, 'current_memory': 80, 'cpu': 40, 'memory': 40, 'current_cost': 100}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertGreaterEqual(payload['data']['simulation']['savings'], 0)
        self.assertEqual(Simulation.objects.count(), 1)

    def test_carbon_and_sustainability_endpoints(self):
        user = CustomUser.objects.create_user(username='carbonuser', password='StrongPass1!')
        self.client.force_login(user)
        carbon_response = self.client.post(
            reverse('optimizer:carbon'),
            data=json.dumps({'cpu': 4, 'memory': 8, 'hours': 3, 'region': 'us-east-1'}),
            content_type='application/json',
        )
        self.assertEqual(carbon_response.status_code, 200)
        self.assertEqual(CarbonFootprint.objects.count(), 1)

        sustainability_response = self.client.get(reverse('optimizer:sustainability'))
        self.assertEqual(sustainability_response.status_code, 200)
        self.assertIn('score', sustainability_response.json()['data']['sustainability'])
        self.assertEqual(SustainabilityScore.objects.count(), 1)

    def test_region_kubernetes_and_chatbot_endpoints(self):
        user = CustomUser.objects.create_user(username='advanceduser', password='StrongPass1!')
        self.client.force_login(user)
        region_response = self.client.post(
            reverse('optimizer:region_advisor'),
            data=json.dumps({'current_region': 'eu-central-1', 'cpu': 4, 'memory': 8, 'hours': 10}),
            content_type='application/json',
        )
        self.assertEqual(region_response.status_code, 200)
        self.assertIn('recommended_region', region_response.json()['data']['region_advice'])
        self.assertEqual(RegionRecommendation.objects.count(), 1)

        k8s_response = self.client.post(
            reverse('optimizer:kubernetes_simulate'),
            data=json.dumps({'cpu': 1, 'memory': 2, 'replicas': 3, 'hours': 6, 'region': 'us-east-1'}),
            content_type='application/json',
        )
        self.assertEqual(k8s_response.status_code, 200)
        self.assertEqual(KubernetesSimulation.objects.count(), 1)

        chatbot_response = self.client.post(
            reverse('optimizer:chatbot'),
            data=json.dumps({'query': 'Give me budget details'}),
            content_type='application/json',
        )
        self.assertEqual(chatbot_response.status_code, 200)
        self.assertIn('response', chatbot_response.json()['data']['chatbot'])
        self.assertEqual(ChatbotInteraction.objects.count(), 1)
