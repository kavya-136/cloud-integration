from decimal import Decimal, ROUND_HALF_UP

from .models import BudgetAlert


def evaluate_alert_status(threshold, current_cost):
    threshold_value = Decimal(str(threshold))
    current_value = Decimal(str(current_cost))
    if threshold_value <= 0:
        return BudgetAlert.ALERT_NORMAL
    ratio = current_value / threshold_value
    if ratio >= Decimal('1'):
        return BudgetAlert.ALERT_CRITICAL
    if ratio >= Decimal('0.8'):
        return BudgetAlert.ALERT_WARNING
    return BudgetAlert.ALERT_NORMAL


def normalize_currency(value):
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
