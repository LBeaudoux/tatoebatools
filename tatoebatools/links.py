import logging
from pathlib import Path

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name

logger = logging.getLogger(__name__)


class Links:
    """The links between the Tatoeba sentences of a pair of languages."""

    _table = "links"

    def __init__(
        self, source_language, target_language, scope="all", data_dir=None
    ):
        # the source language of the links
        self._src_lg = source_language
        # the target language of the links
        self._tgt_lg = target_language
        # rows that are iterated through
        self._sp = scope
        # path of the parent directory of links files
        dp = Path(data_dir) if data_dir else DATA_DIR
        self._dir = dp.joinpath(Links._table)

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = self._dir.joinpath(fname)

        fieldnames = ["sentence_id", "translation_id"]

        try:
            for row in DataFile(fpath, delimiter="\t", text_col=None):
                row = {fieldnames[i]: x for i, x in enumerate(row)}
                yield Link(**row)
        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{Links._table}' table from {self._src_lg} to "
                f"{self._tgt_lg}."
            )

            logger.warning(msg)

    @property
    def source_language(self):
        """Get the source language of these links."""
        return self._src_lg

    @property
    def target_language(self):
        """Get the target language of these links."""
        return self._tgt_lg

    @property
    def stem(self):
        """Get the stem of the file where the links for this language
        pair are saved.
        """
        return f"{self._src_lg}-{self._tgt_lg}_{Links._table}"

    @property
    def filename(self):
        """Get the name of the file where the links for this language
        pair are saved.
        """
        return f"{self.stem}.tsv"

    @property
    def path(self):
        """Get the path where the links are saved for this language pair."""
        return self._dir.joinpath(self.filename)


class Link:
    """A link between a Tatoeba's sentence and its translation."""

    def __init__(self, sentence_id, translation_id):

        self._src_id = sentence_id
        self._tgt_id = translation_id

    @property
    def sentence_id(self):
        """The id of the source sentence."""
        return int(self._src_id)

    @property
    def translation_id(self):
        """The id of the target sentence."""
        return int(self._tgt_id)
