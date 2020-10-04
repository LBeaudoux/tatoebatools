import json
import logging
from datetime import datetime
from pathlib import Path

from pkg_resources import resource_filename

logger = logging.getLogger(__name__)


class Version:
    """A JSON file where the versions of the files are saved.
    The version of a file is the date time string of the downloaded file
    its data derives from.
    """

    _path = Path(resource_filename(__package__, "data/versions.json"))

    def __init__(self):
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
            with open(Version._path) as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        else:
            logger.debug("version datafile loaded")

        return data

    def _save(self):
        """Save the data file."""
        with open(Version._path, "w") as f:
            json.dump(self._dict, f)


version = Version()
