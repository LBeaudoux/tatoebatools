import logging

from tqdm import tqdm

from .links import Links
from .sentences_detailed import SentencesDetailed


class ParallelCorpora:
    """A parallel corpora, i.e. a collection of sentences placed alongside
    their translations.
    """

    def __init__(self, source_language_code, target_language_code):
        # the source language of the parallel corpora
        self._src_lg = source_language_code
        # the target language of the parallel corpora
        self._tgt_lg = target_language_code

        # load the necessary data in memory
        self._load()

    def __iter__(self):

        for lk in Links(self._src_lg, self._tgt_lg):
            yield (
                self._sentences[lk.sentence_id],
                self._translations[lk.translation_id],
            )

    def _load(self):
        """Load the sentences and links in the current source and target
        languages.
        """
        links = Links(self._src_lg, self._tgt_lg)
        src_corpus = SentencesDetailed(self._src_lg)
        tgt_corpus = SentencesDetailed(self._tgt_lg)

        # log a warning if the datafiles don't share a common version
        if not (
            links.version.date()
            == src_corpus.version.date()
            == tgt_corpus.version.date()
        ):
            logging.warning(
                "the versions of the data files difer. an update is advised."
            )

        # load necessary source and target sentences
        sentence_ids, translation_ids = links.ids
        self._sentences = load_corpus(src_corpus, sentence_ids)
        self._translations = load_corpus(tgt_corpus, translation_ids)


def load_corpus(corpus, filtered_sentence_ids):
    """Load chosen sentences from sentences datafile.
    """
    logging.info(f"loading {corpus.language} sentences")

    sentences = {}
    with tqdm(total=len(filtered_sentence_ids)) as pbar:
        for s in corpus:
            if s.sentence_id in filtered_sentence_ids:
                sentences[s.sentence_id] = s
                pbar.update()

    return sentences
