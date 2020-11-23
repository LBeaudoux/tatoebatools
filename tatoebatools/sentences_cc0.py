from datetime import datetime


class SentenceCC0:
    """A sentence from the Tatoeba corpus with a CC0 licence."""

    def __init__(
        self,
        sentence_id,
        lang,
        text,
        date_last_modified,
    ):

        self._id = sentence_id
        self._lg = lang
        self._txt = text
        self._dtlm = date_last_modified

    @property
    def sentence_id(self):
        """Get the id of the sentence."""
        return int(self._id)

    @property
    def lang(self):
        """Get the language of the sentence."""
        return self._lg

    @property
    def text(self):
        """Get the text of the sentence."""
        return self._txt

    @property
    def date_last_modified(self):
        """Get the date of the last modification of the sentence."""
        try:
            dt = datetime.strptime(self._dtlm, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            dt = None
        finally:
            return dt
