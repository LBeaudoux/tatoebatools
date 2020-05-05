from .corpus import Corpus
from .links import Links


class ParallelCorpora:
    """
    """

    def __init__(self, source_language, target_language):

        self._src_lg = source_language
        self._tgt_lg = target_language

    def __iter__(self):

        src_corpus = {s.id: s for s in Corpus(self._src_lg)}
        tgt_corpus = {s.id: s for s in Corpus(self._tgt_lg)}

        links = Links(self._src_lg, self._tgt_lg)

        for lk in links:
            yield (src_corpus[lk.sentence_id], tgt_corpus[lk.translation_id])
