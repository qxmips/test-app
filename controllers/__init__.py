import time
from flask import Config, Flask
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)
def main(config: Config):

    logger.debug("flask: received request")
    return { 'hello': config.get('HELLO_NAME', 'World') }, 200


def ping(value, store: OrderedDict):

    store[value] = time.time()

    return dict(ping=value, values=store)
