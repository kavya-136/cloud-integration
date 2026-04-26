import json


def extract_payload(request):
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError('Invalid JSON payload.') from exc
    return request.POST


def extract_float(value, name, required=True):
    if value in (None, ''):
        if required:
            raise ValueError(f'{name} is required.')
        return None

    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be a number.') from exc

    if parsed < 0:
        raise ValueError(f'{name} must be non-negative.')
    return parsed
