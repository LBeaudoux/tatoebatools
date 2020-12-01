class Link:
    """A link between a Tatoeba's sentence and its translation"""

    def __init__(self, sentence_id, translation_id):

        self._src_id = sentence_id
        self._tgt_id = translation_id

    @property
    def sentence_id(self):
        """The id of the source sentence"""
        return int(self._src_id)

    @property
    def translation_id(self):
        """The id of the target sentence"""
        return int(self._tgt_id)
