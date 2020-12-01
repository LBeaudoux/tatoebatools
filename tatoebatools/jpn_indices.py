class JpnIndex:
    """Each entry is associated with a pair of Japanese/English sentences
    Equivalent of the "B lines" in the Tanaka Corpus file distributed
    by Jim Breen. More info at:
    https://www.edrdg.org/wiki/index.php/Tanaka_Corpus#Current_Format_.28WWWJDIC.29
    """

    def __init__(self, sentence_id, meaning_id, text):
        # sentence_id refers to the id of the Japanese sentence.
        self._sid = sentence_id
        # meaning_id refers to the id of the English sentence.
        self._mid = meaning_id
        #
        self._txt = text

    @property
    def sentence_id(self):
        """Get the id of the Japanese sentence"""
        return int(self._sid)

    @property
    def meaning_id(self):
        """Get the id of the English sentence"""
        return int(self._mid)

    @property
    def text(self):
        """Get the text of the entry"""
        return self._txt
