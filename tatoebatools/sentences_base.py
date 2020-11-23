from .utils import is_na


class SentenceBase:
    """The base of a sentence from the Tatoeba corpus

    A sentence is based on another if it has been initially added as a
    translation.

    The base of a sentence is equal to:
    - 0 when the sentence is original (i.e. not based on another)
    - the sentence id it is based upon when this one is available
    - None when the information about the base is not available
    """

    def __init__(
        self,
        sentence_id,
        base_of_the_sentence,
    ):

        self._id = sentence_id
        self._bs = base_of_the_sentence

    @property
    def sentence_id(self):
        """Get the id of the sentence"""
        return int(self._id)

    @property
    def base_of_the_sentence(self):
        """Get the base of the sentence"""
        return int(self._bs) if not is_na(self._bs) else None
