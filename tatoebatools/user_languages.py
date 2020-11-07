import logging
from pathlib import Path

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name

logger = logging.getLogger(__name__)


class UserLanguages:
    """The self-reported skill levels of members in individual languages."""

    _table = "user_languages"

    def __init__(self, language, scope="all", data_dir=None):

        self._lg = language
        # rows that are iterated through
        self._sp = scope
        # the directory where the user languages are saved
        dp = Path(data_dir) if data_dir else DATA_DIR
        self._dir = dp.joinpath(UserLanguages._table)

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = self._dir.joinpath(fname)

        try:
            fieldnames = [
                "lang",
                "skill_level",
                "username",
                "details",
            ]

            for row in DataFile(fpath, delimiter="\t"):
                row = {fieldnames[i]: x for i, x in enumerate(row)}

                yield UserLanguage(**row)

        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{UserLanguages._table}' table."
            )

            logger.warning(msg)

    @property
    def language(self):
        """Get the language of the datafile."""
        return self._lg

    @property
    def stem(self):
        """Get the stem of the name of the datafile"""
        return f"{self._lg}_{UserLanguages._table}"

    @property
    def filename(self):
        """Get the name of the datafile"""
        return f"{self.stem}.tsv"

    @property
    def path(self):
        """Get the path of the datafile."""
        return self._dir.joinpath(self.filename)


class UserLanguage:
    """The self-reported skill level of a user in a language."""

    def __init__(self, lang, skill_level, username, details):
        # the language
        self._lg = lang
        # the leval of the user in this language
        self._skl = skill_level
        # the name of the user
        self._usr = username
        # optional comments
        self._dtl = details

    @property
    def lang(self):
        """Get the language for this user skill."""
        return self._lg

    @property
    def skill_level(self):
        """Get the value of this skill level."""
        return int(self._skl) if self._skl != "\\N" else None

    @property
    def username(self):
        """Get the name of the user who have this language skill."""
        return self._usr if self._usr != "\\N" else None

    @property
    def details(self):
        """Get more details about this user's language skill."""
        return self._dtl
