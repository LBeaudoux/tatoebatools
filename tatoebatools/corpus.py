import logging

from .sentences_detailed import SentencesDetailed
from .tatoebatools import Tatoeba

logger = logging.getLogger(__name__)


class Corpus:
    """A corpus is a collection of all Tatoeba sentences that share a
    common language.
    """

    def __init__(self, language_code, update=True):
        # the language of the sentences
        self._lg = language_code
        # update the local data
        if update:
            Tatoeba().update(["sentences_detailed"], [self._lg], verbose=False)

    def __iter__(self):

        return SentencesDetailed(self._lg).__iter__()
