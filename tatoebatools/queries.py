import csv
import logging
from datetime import datetime

from .config import DATA_DIR
from .utils import lazy_property
from .version import Versions


class Queries:
    """The content of the queries to tatoeba.org.
    """

    _dir = DATA_DIR.joinpath("queries")

    def __init__(self, language):

        self._lg = language

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = ["date", "language", "content"]
                rows = csv.DictReader(f, delimiter=",", fieldnames=fieldnames)
                for i, row in enumerate(rows):

                    if not (i % 2) == 0:  # each query is recorded twice
                        continue

                    if not len(row) == 3:
                        continue

                    q = Query(**row)

                    if not q.content:
                        continue

                    if not len(q.language) in (3, 4):
                        continue

                    yield q

        except OSError:
            logging.exception(f"an error occurred while reading {self.path}")

    @property
    def language(self):
        """Get the language of these queries.
        """
        return self._lg

    @property
    def path(self):
        """Get the path where the queries are saved.
        """
        return Queries._dir.joinpath(self.filename)

    @property
    def filename(self):
        """Get the name of the file where the queries are saved.
        """
        return f"{self._lg}_queries.csv"

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these queries.
        """
        return Versions().get(self.filename)


class Query:
    """A query made to tatoeba.org.
    """

    def __init__(self, date, language, content):

        self._dt = date
        self._lg = language
        self._ct = content

    @lazy_property
    def date(self):
        """The date when the query was made. e.g. '5 Apr 2019'
        """
        return datetime.strptime(self._dt, "%-d %b %Y")

    @lazy_property
    def language(self):
        """The language in which the query has been made, e.g. 'fra'
        """
        return self._lg

    @lazy_property
    def content(self):
        """The content of the query (i.e. the searched text).
        """
        return self._ct
