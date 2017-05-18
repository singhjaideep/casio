from casio.app import create_celery_app

celery = create_celery_app()


@celery.task()
def deliver_calculation(calc, message):
    ctx = {'calc': calc, 'message': message}
    #TODO
    return None
