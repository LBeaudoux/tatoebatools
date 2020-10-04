import logging
from datetime import datetime

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class SentencesCC0:
    """The Tatoeba file containing the sentences with a CC0 license in a given
    language.
    """

    _table = "sentences_CC0"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language, scope="all"):

        # the language code of the sentences (ISO-639 code most of the time)
        self._lg = language
        # rows that are iterated through
        self._sp = scope

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = SentencesCC0._dir.joinpath(fname)

        try:
            fieldnames = [
                "sentence_id",
                "lang",
                "text",
                "date_last_modified",
            ]

            for row in DataFile(fpath, delimiter="\t", text_col=2):
                row = {fieldnames[i]: x for i, x in enumerate(row)}
                yield SentenceCC0(**row)
        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{SentencesCC0._table}' table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences."""
        return self._lg

    @property
    def stem(self):
        """Get the stem of the file of these sentences."""
        return f"{self._lg}_{SentencesCC0._table}"

    @property
    def filename(self):
        """Get the name of the file of these sentences."""
        return f"{self.stem}.tsv"

    @property
    def path(self):
        """Get the path of the sentences' datafile."""
        return SentencesCC0._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these sentences."""
        return version[self.stem]


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
        except ValueError:
            dt = None
        finally:
            return dt
