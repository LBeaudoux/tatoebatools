import json
import logging
from datetime import datetime
from pathlib import Path

from .config import DATA_DIR

logger = logging.getLogger(__name__)


class Version:
    """A JSON file which stores the versions of the local Tatoeba datafiles
    A version is the string of the date when a file was published at
    https://downloads.tatoeba.org
    """

    def __init__(self, data_dir=None):
        """
        Parameters
        ----------
        data_dir : str, optional
            The path of the directory where the Tatoeba data is saved.
            If None, the data is saved into the tatoebatools package
        """
        self._dir = Path(data_dir) if data_dir else DATA_DIR
        # the dict from which versions' values are fetched
        self._dict = self._load()

    def __getitem__(self, filename):

        vs = self._dict.get(filename)

        return datetime.strptime(vs, "%Y-%m-%d %H:%M:%S") if vs else None

    def __setitem__(self, filename, new_version):

        self._dict[filename] = new_version.strftime("%Y-%m-%d %H:%M:%S")
        self._save()

    def __len__(self):

        return len(self._dict)

    def _load(self):
        """Load the data file."""
        try:
            with open(self.path) as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        else:
            logger.debug("version datafile loaded")

        return data

    def _save(self):
        """Save the data file."""
        with open(self.path, "w") as f:
            json.dump(self._dict, f)

    @property
    def path(self):
        """Gets the path of this version file"""
        return self._dir.joinpath("versions.json")

    @property
    def dir(self):
        """Gets the path of the directory where the versions are saved"""
        return self._dir

    @dir.setter
    def dir(self, new_dir_path):
        """Gets the path of the directory where the versions are saved"""
        self._dir = Path(new_dir_path)
        self._dict = self._load()


version = Version()
