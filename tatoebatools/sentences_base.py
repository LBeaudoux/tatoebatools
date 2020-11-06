import logging
from pathlib import Path

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name

logger = logging.getLogger(__name__)


class SentencesBase:
    """The Tatoeba file containing the sentences' bases in a given
    language
    """

    _table = "sentences_base"

    def __init__(self, language, scope="all", data_dir=None):

        # the language code of the sentences (ISO-639 code most of the time)
        self._lg = language
        # rows that are iterated through
        self._sp = scope
        # the directory where the sentence bases are saved
        dp = Path(data_dir) if data_dir else DATA_DIR
        self._dir = dp.joinpath(SentencesBase._table)

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = self._dir.joinpath(fname)

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
        return self._dir.joinpath(self.filename)


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
