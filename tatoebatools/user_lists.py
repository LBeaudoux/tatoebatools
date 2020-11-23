from datetime import datetime


class UserList:
    """A list of sentences built by a Tatoeba user"""

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
        """Get the id of this list"""
        return int(self._id)

    @property
    def username(self):
        """Get the name of the user that built this list"""
        return self._usr

    @property
    def date_created(self):
        """Get the date when this list has been created"""
        try:
            dt = datetime.strptime(self._dcr, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            dt = None
        finally:
            return dt

    @property
    def date_last_modified(self):
        """Get the date when this list has been modified for the last time"""
        try:
            dt = datetime.strptime(self._dlm, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            dt = None
        finally:
            return dt

    @property
    def list_name(self):
        """Get the name of this list"""
        return self._nm

    @property
    def editable_by(self):
        """Get the users that can edit this list"""
        return self._edb
