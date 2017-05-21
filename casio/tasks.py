from casio.app import create_celery_app
celery = create_celery_app()

@celery.task()
def deliver_calculation(calc):
    """
    Offload calculation task to separate process
    """
    result = None
    result = eval(calc)
    return str(result)