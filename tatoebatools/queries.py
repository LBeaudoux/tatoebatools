import logging
from datetime import datetime

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class Queries:
    """The content of the queries to tatoeba.org."""

    _table = "queries"
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
            fpath = Queries._dir.joinpath(fname)

        try:
            fieldnames = ["date", "language", "content"]

            for i, row in enumerate(
                DataFile(fpath, delimiter=",", text_col=-1)
            ):
                row = {fieldnames[i]: x for i, x in enumerate(row)}

                if not (i % 2) == 0:  # each query is recorded twice
                    continue

                q = Query(**row)

                if not q.content:
                    continue

                if not len(q.language) in (3, 4):
                    continue

                yield q

        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{Queries._table}' table in '{self._lg}''"
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of these queries."""
        return self._lg

    @property
    def path(self):
        """Get the path where the queries are saved."""
        return Queries._dir.joinpath(self.filename)

    @property
    def filename(self):
        """Get the name of the file where the queries are saved."""
        return f"{self._lg}_queries.csv"

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these queries."""
        return version[Queries._table]


class Query:
    """A query made to tatoeba.org."""

    def __init__(self, date, language, content):

        self._dt = date
        self._lg = language
        self._ct = content

    @property
    def date(self):
        """The date when the query was made. e.g. '5 Apr 2019'"""
        try:
            date = datetime.strptime(self._dt, "%d %b %Y")
        except ValueError:
            logger.debug(f"{self._dt} is not a valid date")
            return
        else:
            return date.date()

    @property
    def language(self):
        """The language in which the query has been made, e.g. 'fra'"""
        return self._lg

    @property
    def content(self):
        """The content of the query (i.e. the searched text)."""
        return self._ct
