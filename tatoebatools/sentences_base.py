import logging

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class SentencesBase:
    """The Tatoeba file containing the sentences' bases in a given
    language
    """

    _table = "sentences_base"
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
            fpath = SentencesBase._dir.joinpath(fname)

        try:
            fieldnames = [
                "sentence_id",
                "base_of_the_sentence",
            ]

            for row in DataFile(fpath, delimiter="\t"):
                row = {fieldnames[i]: x for i, x in enumerate(row)}
                yield SentenceBase(**row)
        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{SentencesBase._table}' table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences"""
        return self._lg

    @property
    def stem(self):
        """Get the stem of the file of these sentences"""
        return f"{self._lg}_{SentencesBase._table}"

    @property
    def filename(self):
        """Get the name of the file of these sentences"""
        return f"{self.stem}.tsv"

    @property
    def path(self):
        """Get the path of the sentences' datafile"""
        return SentencesBase._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these sentences."""
        return version[self.stem]


class SentenceBase:
    """The base of a sentence from the Tatoeba corpus

    A sentence is based on another if it has been initially added as a
    translation.

    The base of a sentence is equal to:
    - 0 when the sentence is original (i.e. not based on another)
    - the sentence id it is based upon when this one is available
    - None when the information about the base is not available
    """

    def __init__(
        self,
        sentence_id,
        base_of_the_sentence,
    ):

        self._id = sentence_id
        self._bs = base_of_the_sentence

    @property
    def sentence_id(self):
        """Get the id of the sentence"""
        return int(self._id)

    @property
    def base_of_the_sentence(self):
        """Get the base of the sentence"""
        return int(self._bs) if self._bs != "\\N" else None
