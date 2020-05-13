import csv
import logging

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version

logger = logging.getLogger(__name__)


class Transcriptions:
    """The transcriptions in auxiliary or alternative scripts. 
    """

    _table = "transcriptions"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language):

        self._lg = language

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = [
                    "sentence_id",
                    "lang",
                    "script_name",
                    "username",
                    "transcription",
                ]

                rows = csv.DictReader(
                    f, delimiter="\t", escapechar="\\", fieldnames=fieldnames
                )
                for row in rows:
                    yield Transcription(**row)
        except OSError:
            msg = (
                f"no data locally available for the "
                f"'{Transcriptions._table}' table."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the datafile.
        """
        return self._lg

    @property
    def filename(self):
        """Get the name of the datafile.
        """
        return f"{self._lg}_{Transcriptions._table}.tsv"

    @property
    def path(self):
        """Get the path of the datafile.
        """
        return Transcriptions._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data.
        """
        with Version() as vs:
            return vs[self.filename]


class Transcription:
    """A sentence transcription in an auxiliary or alternative script.
    """

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
        """Get the id of the sentence of this transcription.
        """
        return int(self._sid)

    @property
    def lang(self):
        """Get the language for this transcription. 
        """
        return self._lg

    @property
    def script_name(self):
        """Get the name of the script in which this transcription is made. 
        """
        return self._scp

    @property
    def username(self):
        """Get the name of the user who have this language skill. 
        """
        return self._usr

    @property
    def transcription(self):
        """Get the text of this transcription.
        """
        return self._trs