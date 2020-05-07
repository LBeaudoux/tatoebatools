import logging

from tqdm import tqdm

from .corpus import Corpus
from .links import Links
from .utils import lazy_property


class Translations:
    """A parallel corpora, i.e. a collection of sentences placed alongside
    their translations.
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

        # load source and target sentences
        self._sentences = self._load_sentences(self._src_lg, self.sentence_ids)
        self._translations = self._load_sentences(
            self._tgt_lg, self.translation_ids
        )

    def __iter__(self):

        for lk in self._links:
            yield (
                self._sentences[lk.sentence_id],
                self._translations[lk.translation_id],
            )

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

    def _load_sentences(self, language_code, sentence_ids):
        """Load chosen sentences data from corpus.
        """
        logging.info(f"loading {language_code} sentences")

        sentences = {}
        with tqdm(total=len(sentence_ids)) as pbar:
            for s in Corpus(language_code):
                if s.id in sentence_ids:
                    sentences[s.id] = s
                    pbar.update()

        return sentences
