import csv
import logging

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version

logger = logging.getLogger(__name__)


class Audios:
    """The Tatoeba sentences with audio for a given language.
    """

    _table = "sentences_with_audio"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language):
        # the language of the sentences with audio
        self._lg = language

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = [
                    "sentence_id",
                    "username",
                    "license",
                    "attribution_url",
                ]
                rows = csv.DictReader(
                    f, delimiter="\t", escapechar="\\", fieldnames=fieldnames
                )
                for row in rows:
                    yield Audio(**row)
        except OSError:
            msg = (
                f"no data locally available for the '{self.table}' "
                f"table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of these sentences with audio.
        """
        return self._lg

    @property
    def path(self):
        """Get the path where the sentences with audio are saved.
        """
        return Audios._dir.joinpath(self.filename)

    @property
    def filename(self):
        """Get the name of the file where the sentences with audio are saved.
        """
        return f"{self._lg}_{Audios._table}.tsv"

    @lazy_property
    def version(self):
        """Get the version of these sentences with audio.
        """
        with Version() as vs:
            return vs[self.filename]


class Audio:
    """A Tatoeba sentence with audio.
    """

    def __init__(self, sentence_id, username, license, attribution_url):

        self._id = sentence_id
        self._usr = username
        self._lic = license
        self._atr = attribution_url

    @property
    def sentence_id(self):
        """The id of the sentence with audio.
        """
        return int(self._id)

    @property
    def username(self):
        """The username that added the sentence with audio.
        """
        return self._usr

    @property
    def license(self):
        """The license of the sentence with audio.
        """
        return self._lic if self._lic != "\\N" else ""

    @property
    def attribution_url(self):
        """The url to the attrbution of the sentence with audio.
        """
        return self._atr if self._atr != "\\N" else ""
