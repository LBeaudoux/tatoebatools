import csv
import logging
from datetime import datetime

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version

logger = logging.getLogger(__name__)


class SentencesCC0:
    """The Tatoeba file containing the sentences with a CC0 license in a given 
    language.
    """

    _table = "sentences_CC0"
    _dir = DATA_DIR.joinpath(_table)

    def __init__(self, language_code, cc0_only=False):

        # the language code of the sentences (ISO-639 code most of the time)
        self._lg = language_code

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = [
                    "sentence_id",
                    "lang",
                    "text",
                    "date_last_modified",
                ]

                rows = csv.DictReader(
                    f, delimiter="\t", escapechar="\\", fieldnames=fieldnames
                )
                for row in rows:
                    yield SentenceCC0(**row)
        except OSError:
            msg = (
                f"no data locally available for the "
                f"'{SentencesCC0._table}' table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences.
        """
        return self._lg

    @property
    def filename(self):
        """Get the name of the file of these sentences.
        """
        return f"{self._lg}_{SentencesCC0._table}.tsv"

    @property
    def path(self):
        """Get the path of the sentences' datafile.
        """
        return SentencesCC0._dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these sentences.
        """
        with Version() as vs:
            return vs[self.filename]


class SentenceCC0:
    """A sentence from the Tatoeba corpus witha CC0 licence.
    """

    def __init__(
        self, sentence_id, lang, text, date_last_modified,
    ):

        self._id = sentence_id
        self._lg = lang
        self._txt = text
        self._dtlm = date_last_modified

    @property
    def sentence_id(self):
        """Get the id of the sentence.
        """
        return int(self._id)

    @property
    def lang(self):
        """Get the language of the sentence.
        """
        return self._lg

    @property
    def text(self):
        """Get the text of the sentence.
        """
        return self._txt

    @property
    def date_last_modified(self):
        """Get the date of the last modification of the sentence.
        """
        try:
            dt = datetime.strptime(self._dtlm, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = None
        finally:
            return dt
