import logging

from .links import Links
from .sentences_detailed import SentencesDetailed
from .tatoebatools import Tatoeba

logger = logging.getLogger(__name__)


class ParallelCorpus:
    """A parallel corpus of bilingual sentences' pairs

    A parallel corpus between two languages is a collection of the
    Tatoeba sentences in the source language placed alongside their
    translations in the target language.
    """

    def __init__(
        self,
        source_language_code,
        target_language_code,
        update=True,
        verbose=True,
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

        self._update()  # update local data
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
            for lk in Links(self._src_lg, self._tgt_lg):
                if (
                    lk.sentence_id in self._sentences
                    and lk.translation_id in self._translations
                ):
                    yield (
                        self._sentences[lk.sentence_id],
                        self._translations[lk.translation_id],
                    )

    def _update(self):
        """Updates local data required for this parallel corpus"""
        tatoeba = Tatoeba()
        if self._upd:  # if update explicitly demanded
            tatoeba.update(
                ["sentences_detailed", "links"],
                [self._src_lg, self._tgt_lg],
                oriented_pair=True,
                verbose=False,
            )
        else:  # if necessary local data missing
            if not SentencesDetailed(self._src_lg).version:
                tatoeba.update(
                    ["sentences_detailed"],
                    [self._src_lg],
                    verbose=False,
                )
            if not SentencesDetailed(self._tgt_lg).version:
                tatoeba.update(
                    ["sentences_detailed"],
                    [self._tgt_lg],
                    verbose=False,
                )
            if not Links(self._src_lg, self._tgt_lg).version:
                tatoeba.update(
                    ["links"],
                    [self._src_lg, self._tgt_lg],
                    oriented_pair=True,
                    verbose=False,
                )

    def _load(self):
        """Loads the sentences and links from their datafiles"""

        links = Links(self._src_lg, self._tgt_lg)
        src_corpus = SentencesDetailed(self._src_lg)
        tgt_corpus = SentencesDetailed(self._tgt_lg)

        if any(not tbl.version for tbl in (links, src_corpus, tgt_corpus)):
            logger.error(
                f"{self._src_lg}-{self._tgt_lg} parralel corpus: "
                f"missing data file(s). please update your data."
            )
        elif not (
            links.version.date()
            == src_corpus.version.date()
            == tgt_corpus.version.date()
        ):
            logger.error(
                f"{self._src_lg}-{self._tgt_lg} parralel corpus: "
                f"data files' versions difer. please update your data."
            )
        else:
            src_ids, tgt_ids = links.ids
            self._sentences = src_corpus.get(src_ids)
            self._translations = tgt_corpus.get(tgt_ids)
