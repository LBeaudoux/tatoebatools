import logging
from pathlib import Path

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name

logger = logging.getLogger(__name__)


class Tags:
    """The tags associated with each sentence."""

    _table = "tags"

    def __init__(self, language, scope="all", data_dir=None):

        # the language code of the sentences (ISO-639 code most of the time)
        self._lg = language
        # rows that are iterated through
        self._sp = scope
        # the directory where the tags files are saved
        dp = Path(data_dir) if data_dir else DATA_DIR
        self._dir = dp.joinpath(Tags._table)

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = self._dir.joinpath(fname)

        try:
            fieldnames = ["sentence_id", "tag_name"]

            for row in DataFile(fpath, delimiter="\t"):
                row = {fieldnames[i]: x for i, x in enumerate(row)}

                yield Tag(**row)

        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{Tags._table}' table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences tagged."""
        return self._lg

    @property
    def stem(self):
        """Get the stem of the file where the tags for this language
        pair are saved.
        """
        return f"{self._lg}_{Tags._table}"

    @property
    def filename(self):
        """Get the name of the file of these tagged sentences."""
        return f"{self.stem}.tsv"

    @property
    def path(self):
        """Get the path of the tagged sentences' datafile."""
        return self._dir.joinpath(self.filename)


class Tag:
    """A tag associated to a sentence from the Tatoeba corpus."""

    def __init__(
        self,
        sentence_id,
        tag_name,
    ):

        self._id = sentence_id
        self._tag = tag_name

    @property
    def sentence_id(self):
        """Get the id of the sentence tagged."""
        return int(self._id)

    @property
    def tag_name(self):
        """Get the name of the tag."""
        return self._tag
