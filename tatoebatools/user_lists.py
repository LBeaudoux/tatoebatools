import csv
import logging
from datetime import datetime

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version

logger = logging.getLogger(__name__)


class UserLists:
    """The lists of sentences that the users have built. 
    """

    _table = "user_lists"
    _dir = DATA_DIR.joinpath(_table)
    _filename = f"{_table}.csv"
    _path = _dir.joinpath(_filename)

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = [
                    "list_id",
                    "username",
                    "date_created",
                    "date_last_modified",
                    "list_name",
                    "editable_by",
                ]

                rows = csv.DictReader(
                    f, delimiter="\t", escapechar="\\", fieldnames=fieldnames
                )
                for row in rows:
                    yield UserList(**row)
        except OSError:
            msg = (
                f"no data locally available for the '{UserLists._table}' "
                f"table."
            )

            logger.warning(msg)

    @property
    def filename(self):
        """Get the name of the file of these tagged sentences.
        """
        return UserLists._filename

    @property
    def path(self):
        """Get the path of the tagged sentences' datafile.
        """
        return UserLists._path

    @lazy_property
    def version(self):
        """Get the version of the downloaded data of these tagged sentences.
        """
        with Version() as vs:
            return vs[UserLists._filename]


class UserList:
    """A list of sentences built by a Tatoeba user.
    """

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
        """Get the id of this list.
        """
        return int(self._id)

    @property
    def username(self):
        """Get the name of the user that built this list.
        """
        return self._usr

    @property
    def date_created(self):
        """Get the date when this list has been created.
        """
        try:
            dt = datetime.strptime(self._dcr, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = None
        finally:
            return dt

    @property
    def date_last_modified(self):
        """Get the date when this list has been modified for the last time.
        """
        try:
            dt = datetime.strptime(self._dlm, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = None
        finally:
            return dt

    @property
    def list_name(self):
        """Get the name of this list.
        """
        return self._nm

    @property
    def editable_by(self):
        """Get the users that can edit this list.
        """
        return self._edb
