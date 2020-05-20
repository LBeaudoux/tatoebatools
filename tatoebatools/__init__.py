import logging

from .tatoeba import Tatoeba

tatoeba = Tatoeba()

logging.basicConfig(level=logging.INFO, format='%(message)s')
