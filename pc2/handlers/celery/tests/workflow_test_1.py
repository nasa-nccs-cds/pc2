from pc2.handlers.celery.app import demo_task, celery_execute

celery_execute.apply_async( args=[ [], {}, {} ], queue="edas" )