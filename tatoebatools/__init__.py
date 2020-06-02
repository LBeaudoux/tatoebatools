import logging

from .corpus import Corpus
from .tatoebatools import Tatoeba
from .parallel_corpus import ParallelCorpus

tatoeba = Tatoeba()
Corpus = Corpus
ParallelCorpus = ParallelCorpus

logging.basicConfig(level=logging.INFO, format="%(message)s")
