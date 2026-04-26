import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser

from .models import AnomalyRecord, CloudDataset, PredictionModel


class MLTests(TestCase):
    def test_predict_requires_authentication(self):
        response = self.client.post(reverse('ml:predict'), data={'cpu': 1, 'memory': 1})
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('ml:predict')}")

    @patch('ml.views.load_model')
    def test_predict_endpoint_for_authenticated_user(self, load_model_mock):
        class PredictionStub:
            def predict(self, features):
                return [23.5]

            def predict_proba(self, features):
                return [[0.2, 0.8]]

        load_model_mock.return_value = PredictionStub()
        user = CustomUser.objects.create_user(username='mluser', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.post(
            reverse('ml:predict'),
            data=json.dumps({'cpu': 3.5, 'memory': 8.0}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['prediction']['predicted_cost'], 23.5)
        self.assertEqual(payload['data']['confidence_score'], 0.8)
        self.assertEqual(PredictionModel.objects.count(), 1)

    @patch('ml.views.load_model', side_effect=FileNotFoundError('Model file not found: /tmp/model.pkl'))
    def test_predict_missing_model_returns_503(self, _):
        user = CustomUser.objects.create_user(username='mluser2', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.post(reverse('ml:predict'), data={'cpu': 2, 'memory': 4})
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()['success'])

    @patch('ml.views.load_model')
    def test_anomaly_endpoint_stores_detection(self, load_model_mock):
        class AnomalyStub:
            classes_ = [-1, 1]

            def predict(self, features):
                return [-1]

            def decision_function(self, features):
                return [-0.7]

        load_model_mock.return_value = AnomalyStub()
        user = CustomUser.objects.create_user(username='mluser3', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.post(
            reverse('ml:anomaly'),
            data=json.dumps({'cpu': 92, 'memory': 87, 'cost': 200}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertTrue(payload['data']['anomaly_detected'])
        self.assertEqual(payload['data']['severity'], 'high')
        self.assertEqual(AnomalyRecord.objects.count(), 1)

    def test_anomaly_requires_authentication(self):
        response = self.client.post(reverse('ml:anomaly'), data={'cpu': 1, 'memory': 1})
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('ml:anomaly')}")

    def test_upload_dataset_json_success(self):
        user = CustomUser.objects.create_user(username='datasetuser', password='StrongPass1!')
        self.client.force_login(user)
        payload = {
            'records': [
                {'cpu': 1.5, 'memory': 2.0, 'cost': 10.0, 'tag': 'api', 'cloud': 'AWS'},
                {'cpu': 2.5, 'memory': 4.0, 'cost': 20.0, 'tag': 'db', 'cloud': 'Azure'},
            ]
        }
        response = self.client.post(
            reverse('ml:upload_dataset'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['data']['count'], 2)
        self.assertEqual(CloudDataset.objects.count(), 2)

    def test_upload_dataset_requires_authentication(self):
        response = self.client.post(
            reverse('ml:upload_dataset'),
            data=json.dumps({'records': []}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)

    def test_upload_dataset_invalid_payload_fails(self):
        user = CustomUser.objects.create_user(username='datasetuser2', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.post(
            reverse('ml:upload_dataset'),
            data='{"records":"invalid"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
