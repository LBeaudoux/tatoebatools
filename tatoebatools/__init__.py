import logging

from .tatoebatools import Tatoeba
from .parallel_corpora import ParallelCorpora

tatoeba = Tatoeba()
ParallelCorpora = ParallelCorpora

logging.basicConfig(level=logging.INFO, format="%(message)s")
