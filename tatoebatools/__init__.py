import logging

from .corpus import Corpus
from .parallel_corpus import ParallelCorpus
from .tatoebatools import Tatoeba

tatoeba = Tatoeba()
Corpus = Corpus
ParallelCorpus = ParallelCorpus

logging.basicConfig(level=logging.INFO, format="%(message)s")
