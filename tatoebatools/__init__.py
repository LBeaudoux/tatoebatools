import logging

from .tatoebatools import Tatoeba

logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)

tatoeba = Tatoeba()


class ParallelCorpus:
    """A parallel corpus of sentences' pairs

    A parallel corpus between two languages is a collection of the
    Tatoeba sentences in the source language placed alongside their
    translations in the target language.
    """

    def __init__(
        self,
        source_language_code,
        target_language_code,
        update=True,
        verbose=False,
    ):
        """
        Parameters
        ----------
        source_language_code : str
            The ISO 639-3 code of the parallel corpus' source language
        target_language_code : str
             The ISO 639-3 code of the parallel corpus' target language
        update : bool, optional
            Whether an update of the local data is forced or not, by
            default True
        verbose : bool, optional
            The verbosity of the logging, by default True
        """

        self._src_lg = source_language_code
        self._tgt_lg = target_language_code
        self._upd = update
        self._vb = verbose

        # the source sentences
        self._sentences = {}
        # the target sentences
        self._translations = {}

        self._load()  # load the sentences' data in memory

    def __iter__(self):
        """
        Yields
        -------
        tuple
            the SentenceDetailed instances of both the source sentence
            and its translation
        """

        if self._sentences and self._translations:
            for lk in tatoeba.links(
                self._src_lg, self._tgt_lg, update=False, verbose=False
            ):
                if (
                    lk.sentence_id in self._sentences
                    and lk.translation_id in self._translations
                ):
                    yield (
                        self._sentences[lk.sentence_id],
                        self._translations[lk.translation_id],
                    )

    def _load(self):
        """Loads necessary sentences and links data"""
        # get ids of source sentences and target sentences
        source_ids = set()
        target_ids = set()
        for lk in tatoeba.links(
            self._src_lg, self._tgt_lg, update=self._upd, verbose=self._vb
        ):
            source_ids.add(lk.sentence_id)
            target_ids.add(lk.translation_id)

        # load necessary source and target sentences
        self._sentences = {
            s.sentence_id: s
            for s in tatoeba.sentences_detailed(
                self._src_lg, update=self._upd, verbose=self._vb
            )
            if s.sentence_id in source_ids
        }
        self._translations = {
            s.sentence_id: s
            for s in tatoeba.sentences_detailed(
                self._tgt_lg, update=self._upd, verbose=self._vb
            )
            if s.sentence_id in target_ids
        }
