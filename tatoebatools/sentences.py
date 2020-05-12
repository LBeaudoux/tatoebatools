import csv
import logging
from datetime import datetime

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version

logger = logging.getLogger(__name__)


class Sentences:
    """The Tatoeba file containing the detailed sentences in a given language.
    """

    def __init__(self, language_code, cc0_only=False):

        # the language code of the sentences (ISO-639 code most of the time)
        self._lg = language_code
        # if only sentences with a CC0 license are selected
        self._cc0 = cc0_only

    def __iter__(self):

        try:
            with open(self.path) as f:

                rows = csv.DictReader(
                    f, delimiter="\t", fieldnames=self.fieldnames
                )
                for row in rows:
                    if self._cc0:
                        yield SentenceCC0(**row)
                    else:
                        yield Sentence(**row)
        except OSError:
            msg = (
                f"no data locally available for the '{self.table}' "
                f"table in {self._lg}."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the sentences.
        """
        return self._lg

    @property
    def table(self):
        """Get the name of the table from which these sentences are extracted.
        """
        if self._cc0:
            return "sentences_CC0"
        else:
            return "sentences_detailed"

    @property
    def fieldnames(self):
        """Get the field names for this table.
        """
        res = ["sentence_id", "lang", "text"]
        if not self._cc0:
            res.extend(["username", "date_added"])
        res.append("date_last_modified")

        return res

    @property
    def filename(self):
        """Get the name of the file of these sentences.
        """
        return f"{self._lg}_{self.table}.tsv"

    @property
    def path(self):
        """Get the path of the sentences' datafile.
        """
        table_dir = DATA_DIR.joinpath(self.table)

        return table_dir.joinpath(self.filename)

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these sentences.
        """
        with Version() as vs:
            return vs[self.filename]


class Sentence:
    """A sentence from the Tatoeba corpus.
    """

    def __init__(
        self,
        sentence_id,
        lang,
        text,
        username,
        date_added,
        date_last_modified,
    ):

        self._id = sentence_id
        self._lg = lang
        self._txt = text
        self._usr = username
        self._dtad = date_added
        self._dtlm = date_last_modified

    @property
    def id(self):
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
    def username(self):
        """Get the name of the author of the sentence.
        """
        return self._usr if self._usr != "\\N" else ""

    @property
    def date_added(self):
        """Get the date of the addition of the sentence.
        """
        try:
            dt = datetime.strptime(self._dtad, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = None
        finally:
            return dt

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
    def id(self):
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
