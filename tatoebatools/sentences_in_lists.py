class SentenceInList:
    """A sentence from the Tatoeba corpus which is in a list"""

    def __init__(self, list_id, sentence_id):

        self._lid = list_id
        self._sid = sentence_id

    @property
    def list_id(self):
        """Get the id of the list"""
        return int(self._lid)

    @property
    def sentence_id(self):
        """Get the id of the sentence"""
        return int(self._sid)
