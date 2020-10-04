import logging

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class SentencesInLists:
    """The Tatoeba sentences that are contained in a list."""

    _table = "sentences_in_lists"
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
            fpath = SentencesInLists._dir.joinpath(fname)

        fieldnames = [
            "list_id",
            "sentence_id",
        ]

        try:
            for row in DataFile(fpath, delimiter="\t"):
                row = {fieldnames[i]: x for i, x in enumerate(row)}

                yield SentenceInList(**row)

        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{SentencesInLists._table}' table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences."""
        return self._lg

    @property
    def stem(self):
        """Get the stem of the name of the datafile"""
        return f"{self._lg}_{SentencesInLists._table}"

    @property
    def filename(self):
        """Get the name of the datafile"""
        return f"{self.stem}.tsv"

    @property
    def path(self):
        """Get the path of the datafile."""
        return SentencesInLists._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these sentences"""
        return version[self.stem]


class SentenceInList:
    """A sentence from the Tatoeba corpus which is in a list."""

    def __init__(self, list_id, sentence_id):

        self._lid = list_id
        self._sid = sentence_id

    @property
    def list_id(self):
        """Get the id of the list."""
        return int(self._lid)

    @property
    def sentence_id(self):
        """Get the id of the sentence."""
        return int(self._sid)
