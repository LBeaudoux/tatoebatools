import logging

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class Transcriptions:
    """The transcriptions in auxiliary or alternative scripts."""

    _table = "transcriptions"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language, scope="all"):

        self._lg = language
        # rows that are iterated through
        self._sp = scope

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = Transcriptions._dir.joinpath(fname)

        try:
            fieldnames = [
                "sentence_id",
                "lang",
                "script_name",
                "username",
                "transcription",
            ]

            for row in DataFile(fpath, delimiter="\t"):
                row = {fieldnames[i]: x for i, x in enumerate(row)}

                yield Transcription(**row)

        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{Transcriptions._table}' table."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the datafile."""
        return self._lg

    @property
    def stem(self):
        """Get the stem of the name of the datafile."""
        return f"{self._lg}_{Transcriptions._table}"

    @property
    def filename(self):
        """Get the name of the datafile."""
        return f"{self.stem}.tsv"

    @property
    def path(self):
        """Get the path of the datafile."""
        return Transcriptions._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data."""
        return version[self.stem]


class Transcription:
    """A sentence transcription in an auxiliary or alternative script."""

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
        """Get the id of the sentence of this transcription."""
        return int(self._sid)

    @property
    def lang(self):
        """Get the language for this transcription."""
        return self._lg

    @property
    def script_name(self):
        """Get the name of the script in which this transcription is made."""
        return self._scp

    @property
    def username(self):
        """Get the name of the user who have this language skill."""
        return self._usr

    @property
    def transcription(self):
        """Get the text of this transcription."""
        return self._trs
