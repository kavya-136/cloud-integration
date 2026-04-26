from django.utils import timezone


def next_shutdown_time(schedules):
    now = timezone.now()
    future = [schedule.scheduled_time for schedule in schedules if schedule.is_active and schedule.scheduled_time >= now]
    return min(future) if future else None
