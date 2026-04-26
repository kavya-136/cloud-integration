from django.http import JsonResponse


def success_response(payload=None, status=200, message=None):
    payload = {} if payload is None else payload
    body = {'success': True, 'data': payload}
    if message:
        body['message'] = message
    return JsonResponse(body, status=status)


def error_response(status=400, error=None, code=None):
    messages = {
        400: 'Invalid request.',
        404: 'Resource not found.',
        405: 'Method not allowed.',
        500: 'Internal server error.',
        503: 'Service unavailable.',
    }
    custom_messages = {
        'budget_not_set': 'Budget threshold not configured.',
        'invalid_dataset_payload': 'Invalid dataset payload.',
        'empty_dataset': 'No dataset records provided.',
        'invalid_dataset_format': 'Invalid dataset format.',
        'invalid_threshold': 'Threshold must be a non-negative number.',
        'invalid_current_cost': 'Current cost must be a non-negative number.',
        'invalid_schedule_name': 'Schedule name is required.',
        'invalid_scheduled_time': 'Scheduled time must be a valid ISO datetime.',
        'invalid_boolean': 'Boolean value expected.',
        'invalid_integer': 'Integer value expected.',
        'invalid_query': 'Query is required.',
    }
    error_message = custom_messages.get(code) or messages.get(status, 'Request failed.')
    error_code = code or {
        400: 'invalid_request',
        404: 'not_found',
        405: 'method_not_allowed',
        500: 'internal_error',
        503: 'service_unavailable',
    }.get(status, 'request_failed')
    return JsonResponse({'success': False, 'error': error_message, 'code': error_code}, status=status)
