import logging

from .sentences_detailed import SentencesDetailed
from .tatoebatools import Tatoeba

logger = logging.getLogger(__name__)


class Corpus:
    """A corpus of sentences

    The corpus of a language is the collection of all Tatoeba sentences
    in this language.
    """

    def __init__(self, language_code, update=True):
        """
        Parameters
        ----------
        language_code : str
            The ISO 639-3 code of the corpus' language
        update : bool, optional
            Whether an update of the local data is forced or not, by
            default True
        """
        self._lg = language_code

        if update or not SentencesDetailed(self._lg).version:
            Tatoeba().update(["sentences_detailed"], [self._lg], verbose=False)

    def __iter__(self):
        """
        Returns
        -------
        iterator
            An iterator of SentenceDetailed instances.
        """

        return SentencesDetailed(self._lg).__iter__()
