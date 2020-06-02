import logging

from .links import Links
from .sentences_detailed import SentencesDetailed
from .tatoebatools import Tatoeba

logger = logging.getLogger(__name__)


class ParallelCorpora:
    """A parallel corpora, i.e. the collection of all Tatoeba sentences 
    in a source language placed alongside their translations in a target 
    language.
    """

    def __init__(
        self,
        source_language_code,
        target_language_code,
        update=True,
        verbose=True,
    ):
        # the source language of the parallel corpora
        self._src_lg = source_language_code
        # the target language of the parallel corpora
        self._tgt_lg = target_language_code
        # whether or not updates must be checked for
        self._upd = update
        # verbosity
        self._vb = verbose
        # the source sentences
        self._sentences = {}
        # the target sentences
        self._translations = {}

        # load the necessary data in memory
        self._load()

    def __iter__(self):

        if self._sentences and self._translations:
            for lk in Links(self._src_lg, self._tgt_lg):
                yield (
                    self._sentences[lk.sentence_id],
                    self._translations[lk.translation_id],
                )

    def _load(self):
        """Load the sentences and links in the current source and target
        languages.
        """
        # update local data required for these parallel corpora
        if self._upd:
            tables_to_update = ["sentences_detailed", "links"]
            lang_to_update = [self._src_lg, self._tgt_lg]
            Tatoeba().update(tables_to_update, lang_to_update, verbose=False)

        links = Links(self._src_lg, self._tgt_lg)
        src_corpus = SentencesDetailed(self._src_lg)
        tgt_corpus = SentencesDetailed(self._tgt_lg)

        if any(not tbl.version for tbl in (links, src_corpus, tgt_corpus)):
            logger.error(
                f"{self._src_lg}-{self._tgt_lg} parralel corpora: "
                f"missing data file(s). please update your data."
            )
        elif not (
            links.version.date()
            == src_corpus.version.date()
            == tgt_corpus.version.date()
        ):
            logger.error(
                f"{self._src_lg}-{self._tgt_lg} parralel corpora: "
                f"data files' versions difer. please update your data."
            )
        else:
            # load necessary source and target sentences
            src_ids, tgt_ids = links.ids
            self._sentences = src_corpus.get(src_ids, verbose=self._vb)
            self._translations = tgt_corpus.get(tgt_ids, verbose=self._vb)
