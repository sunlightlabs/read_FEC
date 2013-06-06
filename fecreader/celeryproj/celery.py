# following example from here: http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#next-steps 

from __future__ import absolute_import
from kombu import Exchange, Queue
from celery import Celery

celery = Celery('celeryproj.celery',
                broker='redis://localhost',
                backend='redis://localhost',
                include=['celeryproj.tasks'])

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_QUEUES = (
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('slow',  Exchange('media'),   routing_key='slow'),
        Queue('fast',  Exchange('media'),   routing_key='fast'),
    ),
    CELERY_DEFAULT_QUEUE = 'default',
    CELERY_DEFAULT_EXCHANGE_TYPE = 'direct',
    CELERY_DEFAULT_ROUTING_KEY = 'default',
    CELERYD_MAX_TASKS_PER_CHILD=10,
    
)

if __name__ == '__main__':
    celery.start()
    
# http://stackoverflow.com/questions/9167663/celery-per-task-concurrency-limits-of-workers-per-task

