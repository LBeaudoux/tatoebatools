import logging

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class JpnIndices:
    """Equivalent of the "B lines" in the Tanaka Corpus file distributed
    by Jim Breen. For more info see:
    https://www.edrdg.org/wiki/index.php/Tanaka_Corpus#Current_Format_.28WWWJDIC.29
    Each entry is associated with a pair of Japanese/English sentences.
    """

    _table = "jpn_indices"
    _filename = f"jpn_{_table}.tsv"
    _dir = DATA_DIR.joinpath(_table)
    _path = _dir.joinpath(_filename)

    def __init__(self, scope="all"):

        self._sp = scope

    def __iter__(self):

        if self._sp == "all":
            fpath = JpnIndices._path
        else:
            fname = get_extended_name(JpnIndices._path, self._sp)
            fpath = JpnIndices._dir.joinpath(fname)

        fieldnames = [
            "sentence_id",
            "meaning_id",
            "text",
        ]

        try:
            for row in DataFile(fpath, delimiter="\t", text_col=-1):
                row = {fieldnames[i]: x for i, x in enumerate(row)}
                yield JpnIndex(**row)
        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{JpnIndices._table}' table."
            )

            logger.warning(msg)

    @property
    def filename(self):
        """Get the name of the datafile."""
        return JpnIndices._filename

    @property
    def path(self):
        """Get the path of the datafile."""
        return JpnIndices._path

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these sentences."""
        return version[JpnIndices._table]


class JpnIndex:
    """Each entry is associated with a pair of Japanese/English sentences."""

    def __init__(self, sentence_id, meaning_id, text):
        # sentence_id refers to the id of the Japanese sentence.
        self._sid = sentence_id
        # meaning_id refers to the id of the English sentence.
        self._mid = meaning_id
        #
        self._txt = text

    @property
    def sentence_id(self):
        """Get the id of the Japanese sentence."""
        return int(self._sid)

    @property
    def meaning_id(self):
        """Get the id of the English sentence."""
        return int(self._mid)

    @property
    def text(self):
        """Get the text of the entry."""
        return self._txt
