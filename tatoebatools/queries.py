import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Query:
    """A query made to tatoeba.org"""

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
        """The content of the query (i.e. the searched text)"""
        return self._ct
