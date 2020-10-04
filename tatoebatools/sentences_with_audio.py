import logging

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class SentencesWithAudio:
    """The Tatoeba sentences with audio for a given language."""

    _table = "sentences_with_audio"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language, scope="all"):
        # the language of the sentences with audio
        self._lg = language
        # rows that are iterated through
        self._sp = scope

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = SentencesWithAudio._dir.joinpath(fname)

        try:
            fieldnames = [
                "sentence_id",
                "username",
                "license",
                "attribution_url",
            ]

            for row in DataFile(fpath, delimiter="\t"):
                row = {fieldnames[i]: x for i, x in enumerate(row)}

                yield SentenceWithAudio(**row)

        except NoDataFile:
            msg = (
                f"no '{self._sp}'data locally available for the '{self.table}'"
                f" table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of these sentences with audio."""
        return self._lg

    @property
    def path(self):
        """Get the path where the sentences with audio are saved."""
        return SentencesWithAudio._dir.joinpath(self.filename)

    @property
    def stem(self):
        """Get the stem of the name of the file where the sentences
        with audio are saved
        """
        return f"{self._lg}_{SentencesWithAudio._table}"

    @property
    def filename(self):
        """Get the name of the file where the sentences with audio
        are saved
        """
        return f"{self.stem}.tsv"

    @lazy_property
    def version(self):
        """Get the version of these sentences with audio"""
        return version[self.stem]


class SentenceWithAudio:
    """A Tatoeba sentence with audio."""

    def __init__(self, sentence_id, username, license, attribution_url):

        self._id = sentence_id
        self._usr = username
        self._lic = license
        self._atr = attribution_url

    @property
    def sentence_id(self):
        """The id of the sentence with audio."""
        return int(self._id)

    @property
    def username(self):
        """The username that added the sentence with audio."""
        return self._usr

    @property
    def license(self):
        """The license of the sentence with audio."""
        return self._lic if self._lic != "\\N" else ""

    @property
    def attribution_url(self):
        """The url to the attrbution of the sentence with audio."""
        return self._atr if self._atr != "\\N" else ""
