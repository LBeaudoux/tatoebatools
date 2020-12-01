from datetime import datetime

from .utils import is_na


class SentenceDetailed:
    """A sentence from the Tatoeba corpus"""

    def __init__(
        self,
        sentence_id,
        lang,
        text,
        username,
        date_added,
        date_last_modified,
    ):

        self._id = sentence_id
        self._lg = lang
        self._txt = text
        self._usr = username
        self._dtad = date_added
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
    def username(self):
        """Get the name of the author of the sentence."""
        return self._usr if not is_na(self._usr) else None

    @property
    def date_added(self):
        """Get the date of the addition of the sentence."""
        try:
            dt = datetime.strptime(self._dtad, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            dt = None
        finally:
            return dt

    @property
    def date_last_modified(self):
        """Get the date of the last modification of the sentence."""
        try:
            dt = datetime.strptime(self._dtlm, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            dt = None
        finally:
            return dt
