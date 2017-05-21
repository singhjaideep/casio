from flask import Flask, flash,redirect,request,url_for,render_template
from celery import Celery
from casio.extensions import mail#, csrf

CELERY_TASK_LIST = [
    'casio.tasks',
]

def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)
    
    if settings_override:
        app.config.update(settings_override)
        
    extensions(app)

    @app.route('/', methods=["GET", "POST"])
    def index():
        calc=error=None
        if request.method == "POST":
            from casio.tasks import deliver_calculation #prevent circular import?
            result = deliver_calculation.delay(request.form.get('calc'))
            flash('Thanks, expect a result shortly.', 'success')
            calc=result.wait()
            #return redirect(url_for('calculate.index'))
        return render_template("main_page.html",calc=calc,error=error)

    return app

def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    mail.init_app(app)
    #csrf.init_app(app)

    return None

def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

