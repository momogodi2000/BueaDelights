from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-pending-transactions': {
        'task': 'backed.tasks.check_pending_transactions',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}