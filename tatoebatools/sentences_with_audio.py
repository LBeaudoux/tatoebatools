from .utils import is_na


class SentenceWithAudio:
    """A Tatoeba sentence with audio"""

    def __init__(
        self, sentence_id, audio_id, username, license, attribution_url
    ):

        self._id = sentence_id
        self._aid = audio_id
        self._usr = username
        self._lic = license
        self._atr = attribution_url

    @property
    def sentence_id(self):
        """The id of the sentence with audio"""
        return int(self._id)

    @property
    def audio_id(self):
        """The audio id of the sentence with audio"""
        return int(self._aid)

    @property
    def username(self):
        """The username that added the sentence with audio"""
        return self._usr

    @property
    def license(self):
        """The license of the sentence with audio"""
        return self._lic if not is_na(self._lic) else None

    @property
    def attribution_url(self):
        """The url to the attrbution of the sentence with audio"""
        return self._atr if not is_na(self._atr) else None
