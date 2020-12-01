class Tag:
    """A tag associated to a sentence from the Tatoeba corpus."""

    def __init__(
        self,
        sentence_id,
        tag_name,
    ):

        self._id = sentence_id
        self._tag = tag_name

    @property
    def sentence_id(self):
        """Get the id of the sentence tagged."""
        return int(self._id)

    @property
    def tag_name(self):
        """Get the name of the tag."""
        return self._tag
