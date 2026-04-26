import csv
import json
from io import StringIO

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST

from cloud_optimizer.request_utils import extract_float, extract_payload
from cloud_optimizer.response_utils import error_response, success_response

from .model_loader import load_model
from .models import AnomalyRecord, CloudDataset, PredictionModel


@login_required
@require_POST
def predict_view(request):
    try:
        payload = extract_payload(request)
        cpu, memory = _extract_cpu_memory(payload)
        model = load_model('prediction')
        prediction = model.predict([[cpu, memory]])
        confidence = _extract_confidence(model, [[cpu, memory]])
    except ValueError:
        return error_response(status=400)
    except FileNotFoundError:
        return error_response(status=503)
    except Exception:
        return error_response(status=500)

    prediction_value = float(prediction[0])
    PredictionModel.objects.create(
        user=request.user,
        input_data={'cpu': cpu, 'memory': memory},
        prediction_result={'predicted_cost': prediction_value},
        confidence_score=confidence,
    )
    return success_response(
        {
            'prediction': {'predicted_cost': prediction_value},
            'confidence_score': confidence,
        }
    )


@login_required
@require_POST
def anomaly_view(request):
    try:
        payload = extract_payload(request)
        cpu, memory = _extract_cpu_memory(payload)
        cost = extract_float(payload.get('cost'), 'cost', required=False)
        model = load_model('anomaly')
        features = [[cpu, memory]] if cost is None else [[cpu, memory, cost]]
        anomaly_value = int(model.predict(features)[0])
        anomaly_detected = _is_anomaly(model, anomaly_value)
        if hasattr(model, 'decision_function'):
            score = float(model.decision_function(features)[0])
        else:
            score = 0.0
        severity = _severity_from_score(score)
        anomaly_type = 'cost_spike' if cost and anomaly_detected else 'resource_usage'
        explanation = (
            'Potential anomaly detected in current usage patterns.'
            if anomaly_detected
            else 'Current usage appears within expected range.'
        )
    except ValueError:
        return error_response(status=400)
    except FileNotFoundError:
        return error_response(status=503)
    except Exception:
        return error_response(status=500)

    AnomalyRecord.objects.create(
        user=request.user,
        input_data={'cpu': cpu, 'memory': memory, 'cost': cost},
        anomaly_detected=anomaly_detected,
        anomaly_type=anomaly_type if anomaly_detected else 'none',
        severity=severity,
        explanation=explanation,
    )

    return success_response(
        {
            'anomaly_detected': anomaly_detected,
            'anomaly_type': anomaly_type if anomaly_detected else 'none',
            'severity': severity,
            'explanation': explanation,
        }
    )


@login_required
@require_POST
def upload_dataset_view(request):
    try:
        records = _extract_records(request)
    except ValueError:
        return error_response(status=400, code='invalid_dataset_payload')

    if not records:
        return error_response(status=400, code='empty_dataset')

    dataset_rows = []
    for record in records:
        try:
            dataset_rows.append(
                CloudDataset(
                    user=request.user,
                    cpu=float(record['cpu']),
                    memory=float(record['memory']),
                    cost=float(record['cost']),
                    tag=str(record['tag']).strip(),
                    cloud=str(record['cloud']).strip(),
                )
            )
        except (KeyError, TypeError, ValueError):
            return error_response(
                status=400,
                code='invalid_dataset_format',
            )

    with transaction.atomic():
        CloudDataset.objects.bulk_create(dataset_rows)

    return success_response({'count': len(dataset_rows)}, status=201, message='Dataset uploaded successfully.')


def _extract_records(request):
    if request.content_type and 'application/json' in request.content_type:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError('Invalid JSON payload.') from exc

        if isinstance(payload, dict):
            records = payload.get('records')
        else:
            records = payload
        if not isinstance(records, list):
            raise ValueError('JSON payload must be a list or include a records list.')
        return records

    dataset_file = request.FILES.get('dataset')
    if not dataset_file:
        raise ValueError('Upload a dataset file or send JSON payload.')

    try:
        decoded_data = dataset_file.read().decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError('Dataset file must be UTF-8 encoded.') from exc

    if dataset_file.name.lower().endswith('.json'):
        try:
            records = json.loads(decoded_data)
        except json.JSONDecodeError as exc:
            raise ValueError('Invalid JSON file.') from exc
        if not isinstance(records, list):
            raise ValueError('JSON dataset file must contain a list of records.')
        return records

    if dataset_file.name.lower().endswith('.csv'):
        reader = csv.DictReader(StringIO(decoded_data))
        return list(reader)

    raise ValueError('Unsupported file format. Use CSV or JSON.')


def _extract_cpu_memory(payload):
    cpu = extract_float(payload.get('cpu'), 'cpu')
    memory = extract_float(payload.get('memory'), 'memory')
    return cpu, memory


def _extract_confidence(model, features):
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(features)
        return float(max(probabilities[0]))
    return 1.0


def _severity_from_score(score):
    if score <= -0.5:
        return 'high'
    if score < 0:
        return 'medium'
    return 'low'


def _is_anomaly(model, value):
    classes = getattr(model, 'classes_', None)
    if classes is not None:
        normalized = {int(c) for c in classes}
        if normalized == {-1, 1}:
            return value == -1
        if normalized == {0, 1}:
            return value == 1
    return value < 0
