import logging
from datetime import datetime

from .config import DATA_DIR
from .datafile import DataFile
from .exceptions import NoDataFile
from .utils import get_extended_name, lazy_property
from .version import version

logger = logging.getLogger(__name__)


class UserLists:
    """The lists of sentences that the users have built."""

    _table = "user_lists"
    _dir = DATA_DIR.joinpath(_table)
    _filename = f"{_table}.csv"
    _path = _dir.joinpath(_filename)

    def __init__(self, scope="all"):

        self._sp = scope

    def __iter__(self):

        if self._sp == "all":
            fpath = self.path
        else:
            fname = get_extended_name(self.path, self._sp)
            fpath = UserLists._dir.joinpath(fname)

        try:
            fieldnames = [
                "list_id",
                "username",
                "date_created",
                "date_last_modified",
                "list_name",
                "editable_by",
            ]

            for row in DataFile(fpath, delimiter="\t", text_col=4):
                row = {fieldnames[i]: x for i, x in enumerate(row)}

                yield UserList(**row)

        except NoDataFile:
            msg = (
                f"no '{self._sp}' data locally available for the "
                f"'{UserLists._table}' table."
            )

            logger.warning(msg)

    @property
    def filename(self):
        """Get the name of the file of these tagged sentences."""
        return UserLists._filename

    @property
    def path(self):
        """Get the path of the tagged sentences' datafile."""
        return UserLists._path

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these tagged sentences."""
        return version[UserLists._table]


class UserList:
    """A list of sentences built by a Tatoeba user."""

    def __init__(
        self,
        list_id,
        username,
        date_created,
        date_last_modified,
        list_name,
        editable_by,
    ):

        self._id = list_id
        self._usr = username
        self._dcr = date_created
        self._dlm = date_last_modified
        self._nm = list_name
        self._edb = editable_by

    @property
    def list_id(self):
        """Get the id of this list."""
        return int(self._id)

    @property
    def username(self):
        """Get the name of the user that built this list."""
        return self._usr

    @property
    def date_created(self):
        """Get the date when this list has been created."""
        try:
            dt = datetime.strptime(self._dcr, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = None
        finally:
            return dt

    @property
    def date_last_modified(self):
        """Get the date when this list has been modified for the last time."""
        try:
            dt = datetime.strptime(self._dlm, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = None
        finally:
            return dt

    @property
    def list_name(self):
        """Get the name of this list."""
        return self._nm

    @property
    def editable_by(self):
        """Get the users that can edit this list."""
        return self._edb
