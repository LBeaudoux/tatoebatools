import logging

from tqdm import tqdm

from .sentences import Sentences
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

        # log a warning if the datafiles don't share a common version
        if not (
            self.links.version.date()
            == self.source_corpus.version.date()
            == self.target_corpus.version.date()
        ):
            logging.warning(
                "the versions of the data files difer. an update is advised."
            )

        # load source and target sentences
        self._sentences = self._load_sentences(
            self.source_corpus, self.links.sentence_ids
        )
        self._translations = self._load_sentences(
            self.target_corpus, self.links.translation_ids
        )

    def __iter__(self):

        for lk in self.links:
            yield (
                self._sentences[lk.sentence_id],
                self._translations[lk.translation_id],
            )

    @lazy_property
    def links(self):
        """Get the instance of the links between the source language and the 
        target language.
        """
        return Links(self._src_lg, self._tgt_lg)

    @lazy_property
    def source_corpus(self):
        """Get the instance of the sentences in the source language.
        """
        return Sentences(self._src_lg)

    @lazy_property
    def target_corpus(self):
        """Get the instance of the sentences in the target language.
        """
        return Sentences(self._tgt_lg)

    def _load_sentences(self, corpus, sentence_ids):
        """Load chosen sentences from sentences datafile.
        """
        logging.info(f"loading {corpus.language} sentences")

        sentences = {}
        with tqdm(total=len(sentence_ids)) as pbar:
            for s in corpus:
                if s.id in sentence_ids:
                    sentences[s.id] = s
                    pbar.update()

        return sentences
