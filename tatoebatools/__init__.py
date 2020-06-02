import logging

from .corpus import Corpus
from .tatoebatools import Tatoeba
from .parallel_corpora import ParallelCorpora

tatoeba = Tatoeba()
Corpus = Corpus
ParallelCorpora = ParallelCorpora

logging.basicConfig(level=logging.INFO, format="%(message)s")
