import logging

from .corpus import Corpus
from .links import Links
from .utils import lazy_property


class ParallelCorpora:
    """A parallel corpora, i.e. a collection of sentences placed alongside
    their translations
    """

    def __init__(self, source_language_code, target_language_code):
        # the source language of the parallel corpora
        self._src_lg = source_language_code
        # the target language of the parallel corpora
        self._tgt_lg = target_language_code
        # the corpus instance containing the source sentences
        self._src_corpus = Corpus(self._src_lg)
        # the corpus instance containing the target sentences
        self._tgt_corpus = Corpus(self._src_lg)
        # the links instance containing the links between sentences
        self._links = Links(self._src_lg, self._tgt_lg)

        # log a warning if the datafiles don't share a common version
        if not (
            self._src_corpus.version.date()
            == self._tgt_corpus.version.date()
            == self._tgt_corpus.version.date()
        ):
            logging.warning(
                "the versions of the data files difer. an update is advised."
            )

    def __iter__(self):

        # load useful sentences from corpora
        logging.info(f"loading {self._src_lg} sentences")
        sentences = {
            s.id: s for s in Corpus(self._src_lg) if s.id in self.sentence_ids
        }

        logging.info(f"loading {self._tgt_lg} sentences")
        translations = {
            s.id: s
            for s in Corpus(self._tgt_lg)
            if s.id in self.translation_ids
        }

        for lk in self._links:
            yield (sentences[lk.sentence_id], translations[lk.translation_id])

    @lazy_property
    def sentence_ids(self):
        """Get the ids of the source sentences.
        """
        return self._links.sentence_ids

    @lazy_property
    def translation_ids(self):
        """Get the ids of the target translations.
        """
        return self._links.translation_ids
