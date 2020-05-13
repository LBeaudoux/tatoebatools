import csv
import logging

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version

logger = logging.getLogger(__name__)


class Tags:
    """The tags associated with each sentence. 
    """

    _table = "tags"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language):

        # the language code of the sentences (ISO-639 code most of the time)
        self._lg = language

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = ["sentence_id", "tag_name"]

                rows = csv.DictReader(
                    f, delimiter="\t", escapechar="\\", fieldnames=fieldnames
                )
                for row in rows:
                    yield Tag(**row)
        except OSError:
            msg = (
                f"no data locally available for the '{Tags._table}' "
                f"table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences tagged.
        """
        return self._lg

    @property
    def filename(self):
        """Get the name of the file of these tagged sentences.
        """
        return f"{self._lg}_{Tags._table}.tsv"

    @property
    def path(self):
        """Get the path of the tagged sentences' datafile.
        """
        return Tags._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these tagged sentences.
        """
        with Version() as vs:
            return vs[self.filename]


class Tag:
    """A tag associated to a sentence from the Tatoeba corpus.
    """

    def __init__(
        self, sentence_id, tag_name,
    ):

        self._id = sentence_id
        self._tag = tag_name

    @property
    def sentence_id(self):
        """Get the id of the sentence tagged.
        """
        return int(self._id)

    @property
    def tag_name(self):
        """Get the name of the tag.
        """
        return self._tag
