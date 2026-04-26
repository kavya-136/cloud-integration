from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from cloud_optimizer.request_utils import extract_float, extract_payload
from cloud_optimizer.response_utils import error_response, success_response

from .budget import evaluate_alert_status, normalize_currency
from .carbon import calculate_carbon_emission
from .chatbot import generate_chatbot_response
from .kubernetes import simulate_kubernetes_cost
from .logic import generate_rightsizing_recommendations
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
from .region import estimate_region_cost, recommend_region
from .scheduler import next_shutdown_time
from .simulator import simulate_cost
from .sustainability import calculate_sustainability_score


def _extract_bool(value, name):
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {'true', '1', 'yes'}:
        return True
    if normalized in {'false', '0', 'no'}:
        return False
    raise ValueError(f'{name} must be a boolean.')


def _extract_int(value, name):
    if value in (None, ''):
        raise ValueError(f'{name} must be an integer.')
    parsed = extract_float(value, name)
    if not parsed.is_integer():
        raise ValueError(f'{name} must be an integer.')
    return int(parsed)


@login_required
@require_POST
def recommendations_view(request):
    try:
        payload = extract_payload(request)
        cpu = extract_float(payload.get('cpu'), 'cpu')
        memory = extract_float(payload.get('memory'), 'memory')
        current_cost = extract_float(payload.get('current_cost', 0), 'current_cost')
    except ValueError:
        return error_response(status=400)

    recommendations = generate_rightsizing_recommendations(cpu, memory, current_cost)

    for recommendation in recommendations:
        potential_savings = recommendation['potential_savings']
        Recommendation.objects.create(
            user=request.user,
            resource_name=recommendation['type'],
            current_cost=current_cost,
            optimized_cost=max(current_cost - potential_savings, 0),
            savings_percent=(potential_savings / current_cost * 100) if current_cost else 0,
            recommendation_text=recommendation['description'],
        )

    return success_response({'recommendations': recommendations})


@login_required
@require_POST
def set_budget_view(request):
    try:
        payload = extract_payload(request)
        threshold = normalize_currency(extract_float(payload.get('threshold'), 'threshold'))
    except ValueError:
        return error_response(status=400, code='invalid_threshold')

    budget = BudgetAlert.objects.filter(user=request.user).order_by('-updated_at').first()
    if budget:
        budget.threshold = threshold
        budget.current_cost = Decimal('0.00')
        budget.alert_status = BudgetAlert.ALERT_NORMAL
        budget.save(update_fields=['threshold', 'current_cost', 'alert_status', 'updated_at'])
    else:
        budget = BudgetAlert.objects.create(
            user=request.user,
            threshold=threshold,
            current_cost=Decimal('0.00'),
            alert_status=BudgetAlert.ALERT_NORMAL,
        )
    return success_response(
        {
            'budget': {
                'threshold': float(budget.threshold),
                'current_cost': float(budget.current_cost),
                'alert_status': budget.alert_status,
            }
        },
        message='Budget threshold saved.',
    )


def _resolve_current_cost(request, payload):
    query_cost = request.GET.get('current_cost')
    value = payload.get('current_cost') if isinstance(payload, dict) else None
    raw_cost = query_cost if query_cost not in (None, '') else value
    if raw_cost in (None, ''):
        latest = Simulation.objects.filter(user=request.user).order_by('-created_at').first()
        if latest:
            return float(latest.current_cost)
        raise ValueError('current_cost is required when no simulation history exists.')
    return extract_float(raw_cost, 'current_cost')


@login_required
@require_GET
def budget_status_view(request):
    budget = BudgetAlert.objects.filter(user=request.user).first()
    if not budget:
        return error_response(status=404, code='budget_not_set')

    try:
        current_cost = normalize_currency(_resolve_current_cost(request, {}))
    except ValueError:
        return error_response(status=400, code='invalid_current_cost')
    status_value = evaluate_alert_status(budget.threshold, current_cost)
    budget.current_cost = current_cost
    budget.alert_status = status_value
    budget.save(update_fields=['current_cost', 'alert_status', 'updated_at'])
    return success_response(
        {
            'budget': {
                'threshold': float(budget.threshold),
                'current_cost': float(budget.current_cost),
                'alert_status': budget.alert_status,
            }
        }
    )


@login_required
@require_POST
def budget_alert_check_view(request):
    budget = BudgetAlert.objects.filter(user=request.user).first()
    if not budget:
        return error_response(status=404, code='budget_not_set')

    try:
        payload = extract_payload(request)
        current_cost = normalize_currency(_resolve_current_cost(request, payload))
    except ValueError:
        return error_response(status=400, code='invalid_current_cost')

    status_value = evaluate_alert_status(budget.threshold, current_cost)
    budget.current_cost = current_cost
    budget.alert_status = status_value
    budget.save(update_fields=['current_cost', 'alert_status', 'updated_at'])
    triggered = status_value in {BudgetAlert.ALERT_WARNING, BudgetAlert.ALERT_CRITICAL}
    return success_response(
        {
            'alert': {
                'triggered': triggered,
                'status': status_value,
                'current_cost': float(current_cost),
                'threshold': float(budget.threshold),
            }
        }
    )


@login_required
@require_POST
def scheduler_set_view(request):
    try:
        payload = extract_payload(request)
        schedule_name = str(payload.get('schedule_name', '')).strip()
        if not schedule_name:
            return error_response(status=400, code='invalid_schedule_name')
        schedule_dt = parse_datetime(str(payload.get('scheduled_time', '')).strip())
        if not schedule_dt:
            return error_response(status=400, code='invalid_scheduled_time')
        if timezone.is_naive(schedule_dt):
            schedule_dt = timezone.make_aware(schedule_dt, timezone.get_current_timezone())
        schedule_id = payload.get('id')
    except ValueError:
        return error_response(status=400, code='invalid_scheduled_time')

    try:
        is_active = _extract_bool(payload.get('is_active', True), 'is_active')
    except ValueError:
        return error_response(status=400, code='invalid_boolean')

    if schedule_id:
        schedule = get_object_or_404(ShutdownSchedule, id=schedule_id, user=request.user)
        schedule.schedule_name = schedule_name
        schedule.scheduled_time = schedule_dt
        schedule.is_active = is_active
        schedule.save(update_fields=['schedule_name', 'scheduled_time', 'is_active'])
    else:
        schedule = ShutdownSchedule.objects.create(
            user=request.user,
            schedule_name=schedule_name,
            scheduled_time=schedule_dt,
            is_active=is_active,
        )
    return success_response(
        {
            'schedule': {
                'id': schedule.id,
                'schedule_name': schedule.schedule_name,
                'scheduled_time': schedule.scheduled_time.isoformat(),
                'is_active': schedule.is_active,
            }
        }
    )


@login_required
@require_GET
def scheduler_list_view(request):
    schedules = list(ShutdownSchedule.objects.filter(user=request.user, is_active=True))
    upcoming = next_shutdown_time(schedules)
    return success_response(
        {
            'schedules': [
                {
                    'id': schedule.id,
                    'schedule_name': schedule.schedule_name,
                    'scheduled_time': schedule.scheduled_time.isoformat(),
                    'is_active': schedule.is_active,
                }
                for schedule in schedules
            ],
            'next_shutdown_time': upcoming.isoformat() if upcoming else None,
        }
    )


@login_required
@require_http_methods(['PUT'])
def scheduler_toggle_view(request, schedule_id):
    schedule = get_object_or_404(ShutdownSchedule, id=schedule_id, user=request.user)
    schedule.is_active = not schedule.is_active
    schedule.save(update_fields=['is_active'])
    return success_response(
        {
            'schedule': {
                'id': schedule.id,
                'is_active': schedule.is_active,
            }
        }
    )


@login_required
@require_POST
def simulator_view(request):
    try:
        payload = extract_payload(request)
        cpu = extract_float(payload.get('cpu'), 'cpu')
        memory = extract_float(payload.get('memory'), 'memory')
        current_cpu_value = payload.get('current_cpu')
        current_memory_value = payload.get('current_memory')
        has_current_cpu = current_cpu_value not in (None, '')
        has_current_memory = current_memory_value not in (None, '')
        if has_current_cpu != has_current_memory:
            raise ValueError('current_cpu and current_memory must be provided together.')
        if not has_current_cpu and not has_current_memory:
            current_cpu = cpu
            current_memory = memory
        else:
            current_cpu = extract_float(current_cpu_value, 'current_cpu')
            current_memory = extract_float(current_memory_value, 'current_memory')
        current_cost = extract_float(payload.get('current_cost', 0), 'current_cost')
    except ValueError:
        return error_response(status=400, code='invalid_request')

    simulated_cost = simulate_cost(current_cost, current_cpu, current_memory, cpu, memory)
    savings = round(current_cost - simulated_cost, 2)
    simulation = Simulation.objects.create(
        user=request.user,
        input_params={
            'current_cpu': current_cpu,
            'current_memory': current_memory,
            'cpu': cpu,
            'memory': memory,
        },
        current_cost=normalize_currency(current_cost),
        simulated_cost=normalize_currency(simulated_cost),
        savings=normalize_currency(savings),
    )
    return success_response(
        {
            'simulation': {
                'id': simulation.id,
                'current_cost': float(simulation.current_cost),
                'simulated_cost': float(simulation.simulated_cost),
                'savings': float(simulation.savings),
                'has_savings': simulation.savings > 0,
            }
        }
    )


@login_required
@require_POST
def carbon_view(request):
    try:
        payload = extract_payload(request)
        cpu = extract_float(payload.get('cpu'), 'cpu')
        memory = extract_float(payload.get('memory'), 'memory')
        hours = extract_float(payload.get('hours', 1), 'hours')
        region = str(payload.get('region', 'us-east-1')).strip().lower()
        region_factor = settings.REGION_CARBON_FACTORS.get(region, 1.0)
    except ValueError:
        return error_response(status=400, code='invalid_request')

    carbon_grams = calculate_carbon_emission(
        cpu=cpu,
        memory=memory,
        hours=hours,
        cpu_factor=settings.CARBON_GRAMS_PER_CPU_HOUR,
        memory_factor=settings.CARBON_GRAMS_PER_MEMORY_GB_HOUR,
        region_factor=region_factor,
    )
    record = CarbonFootprint.objects.create(
        user=request.user,
        cpu=cpu,
        memory=memory,
        carbon_grams=carbon_grams,
        region=region,
    )
    cache.delete(f'sustainability-score-{request.user.id}')
    return success_response(
        {
            'carbon': {
                'id': record.id,
                'cpu': cpu,
                'memory': memory,
                'hours': hours,
                'region': region,
                'carbon_grams': carbon_grams,
            }
        }
    )


@login_required
@require_GET
def sustainability_view(request):
    cache_key = f'sustainability-score-{request.user.id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return success_response({'sustainability': cached})

    footprints = CarbonFootprint.objects.filter(user=request.user).order_by('-created_at')
    avg_carbon = footprints.aggregate(avg=Avg('carbon_grams')).get('avg') or 0.0
    latest_footprint = footprints.first()
    latest_region = latest_footprint.region if latest_footprint else 'n/a'
    score = calculate_sustainability_score(avg_carbon_grams=float(avg_carbon))
    breakdown = {
        'average_carbon_grams': round(float(avg_carbon), 4),
        'sample_count': footprints.count(),
        'latest_region': latest_region,
    }
    SustainabilityScore.objects.create(user=request.user, score=score, breakdown=breakdown)
    payload = {'score': score, 'breakdown': breakdown}
    cache.set(cache_key, payload, timeout=60)
    return success_response({'sustainability': payload})


@login_required
@require_POST
def region_advisor_view(request):
    try:
        payload = extract_payload(request)
        current_region = str(payload.get('current_region', 'us-east-1')).strip().lower()
        cpu = extract_float(payload.get('cpu'), 'cpu')
        memory = extract_float(payload.get('memory'), 'memory')
        hours = extract_float(payload.get('hours', 1), 'hours')
    except ValueError:
        return error_response(status=400, code='invalid_request')

    costs = {
        region: estimate_region_cost(cpu, memory, hours, multiplier)
        for region, multiplier in settings.REGION_COST_MAPPING.items()
    }
    recommended_region, difference, savings_percent = recommend_region(costs, current_region)
    recommendation = RegionRecommendation.objects.create(
        user=request.user,
        current_region=current_region,
        recommended_region=recommended_region,
        cost_difference=normalize_currency(difference),
        savings_percent=normalize_currency(savings_percent),
    )
    return success_response(
        {
            'region_advice': {
                'current_region': current_region,
                'recommended_region': recommended_region,
                'cost_difference': float(recommendation.cost_difference),
                'savings_percent': float(recommendation.savings_percent),
                'region_costs': costs,
            }
        }
    )


@login_required
@require_POST
def kubernetes_simulation_view(request):
    try:
        payload = extract_payload(request)
        cpu = extract_float(payload.get('cpu'), 'cpu')
        memory = extract_float(payload.get('memory'), 'memory')
        replicas = _extract_int(payload.get('replicas'), 'replicas')
        hours = extract_float(payload.get('hours', 1), 'hours')
        region = str(payload.get('region', 'us-east-1')).strip().lower()
        region_multiplier = settings.REGION_COST_MAPPING.get(region, 1.0)
    except ValueError:
        return error_response(status=400, code='invalid_request')

    predicted_cost, total_cpu, total_memory = simulate_kubernetes_cost(
        cpu=cpu,
        memory=memory,
        replicas=replicas,
        hours=hours,
        region_multiplier=region_multiplier,
    )
    simulation = KubernetesSimulation.objects.create(
        user=request.user,
        pod_config={'cpu': cpu, 'memory': memory, 'replicas': replicas, 'hours': hours, 'region': region},
        predicted_cost=normalize_currency(predicted_cost),
    )
    return success_response(
        {
            'kubernetes': {
                'id': simulation.id,
                'predicted_cost': float(simulation.predicted_cost),
                'total_cpu': total_cpu,
                'total_memory': total_memory,
                'replicas': replicas,
                'region': region,
            }
        }
    )


@login_required
@require_POST
def chatbot_view(request):
    try:
        payload = extract_payload(request)
        query = str(payload.get('query', '')).strip()
        if not query:
            return error_response(status=400, code='invalid_query')
    except ValueError:
        return error_response(status=400, code='invalid_request')

    latest_budget = BudgetAlert.objects.filter(user=request.user).first()
    latest_sustainability = SustainabilityScore.objects.filter(user=request.user).first()
    latest_region = RegionRecommendation.objects.filter(user=request.user).first()
    context = {
        'budget_status': latest_budget.alert_status if latest_budget else 'normal',
        'sustainability_score': latest_sustainability.score if latest_sustainability else None,
        'recommended_region': latest_region.recommended_region if latest_region else None,
        'recommendation_count': Recommendation.objects.filter(user=request.user).count(),
    }
    reply = generate_chatbot_response(query, settings.CHATBOT_KNOWLEDGE_BASE, context)
    interaction = ChatbotInteraction.objects.create(user=request.user, query=query, response=reply)
    return success_response({'chatbot': {'id': interaction.id, 'query': query, 'response': reply}})
