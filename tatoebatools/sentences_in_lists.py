import csv
import logging

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version

logger = logging.getLogger(__name__)


class SentencesInLists:
    """The Tatoeba sentences that are contained in a list.
    """

    _table = "sentences_in_lists"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language):

        # the language code of the sentences (ISO-639 code most of the time)
        self._lg = language

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = [
                    "list_id",
                    "sentence_id",
                ]

                rows = csv.DictReader(
                    f, delimiter="\t", escapechar="\\", fieldnames=fieldnames
                )
                for row in rows:
                    yield SentenceInList(**row)
        except OSError:
            msg = (
                f"no data locally available for the "
                f"'{SentencesInLists._table}' table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences.
        """
        return self._lg

    @property
    def filename(self):
        """Get the name of the datafile.
        """
        return f"{self._lg}_{SentencesInLists._table}.tsv"

    @property
    def path(self):
        """Get the path of the datafile.
        """
        return SentencesInLists._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these sentences.
        """
        with Version() as vs:
            return vs[self.filename]


class SentenceInList:
    """A sentence from the Tatoeba corpus which is in a list.
    """

    def __init__(self, list_id, sentence_id):

        self._lid = list_id
        self._sid = sentence_id

    @property
    def list_id(self):
        """Get the id of the list.
        """
        return int(self._lid)

    @property
    def sentence_id(self):
        """Get the id of the sentence.
        """
        return int(self._sid)
