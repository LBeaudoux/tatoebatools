class Transcription:
    """A sentence transcription in an auxiliary or alternative script"""

    def __init__(
        self, sentence_id, lang, script_name, username, transcription
    ):

        # the id of the sentence
        self._sid = sentence_id
        # the language of the sentence
        self._lg = lang
        # the name of the script of the transcription defined according to
        # the ISO 15924 standard.
        self._scp = script_name
        # the name of the user indicates the user who last reviewed and
        # possibly modified it. A transcription without a username has not
        # been marked as reviewed.
        self._usr = username
        # the transcription itself
        self._trs = transcription

    @property
    def sentence_id(self):
        """Get the id of the sentence of this transcription"""
        return int(self._sid)

    @property
    def lang(self):
        """Get the language for this transcription"""
        return self._lg

    @property
    def script_name(self):
        """Get the name of the script in which this transcription is made"""
        return self._scp

    @property
    def username(self):
        """Get the name of the user who have this language skill"""
        return self._usr

    @property
    def transcription(self):
        """Get the text of this transcription"""
        return self._trs
