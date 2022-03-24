import connexion

import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from injector import Binder
from flask import abort
from flask.logging import default_handler
from flask_injector import FlaskInjector
from flask_dotenv import DotEnv
from collections import OrderedDict
from healthcheck import HealthCheck

from config import *

# sentry_logging = LoggingIntegration(
#     level=logging.INFO,        # Capture info and above as breadcrumbs
#     event_level=logging.ERROR  # Send errors as events
# )

# sentry_sdk.init(
#     dsn="",
#     integrations=[FlaskIntegration(), sentry_logging],
#     traces_sample_rate=1.0,
#     environment=ENVIRONMENT
# )

app = connexion.App(__name__, specification_dir='.', strict_validation=True)
fapp = app.app  # flask app

app.add_api('apispec.yaml')

env = DotEnv(fapp)
health = HealthCheck(fapp, '/checkhealth')

# logger settings
app_name = 'test-app'
env_name = ENVIRONMENT
#logging.basicConfig(level=logging.INFO, format=f'[{app_name} in {env_name}] ' + default_handler.formatter._fmt)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        log_record['app'] = app_name
        log_record['environment'] = env_name




logger = logging.getLogger()

logHandler = logging.StreamHandler()
#formatter = jsonlogger.JsonFormatter()
formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(app)s %(environment)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

def configure(binder: Binder):
    binder.bind(OrderedDict, OrderedDict())


@app.route('/throw-500')
def throw_500():
    abort(500, 'Test message with 500 code error')

@app.route('/color')
def color():
    return f'<body style="background-color:{app.config.get(color)};"></body>'

@app.route('/throw-real-500')
def throw_real_500():
    a = 10 / 0
    print(a)


inj = FlaskInjector(app=fapp, modules=[configure])

if __name__ == '__main__':
    app.run()
