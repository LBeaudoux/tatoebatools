import json
from datetime import datetime
from pathlib import Path

from pkg_resources import resource_filename


class Version:
    """A JSON file where the versions of the files are saved.
    The version of a file is the date time string of the downloaded file
    its data derives from.
    """

    _path = Path(resource_filename(__package__, "data/versions.json"))

    def __init__(self):

        self._dict = self._load()

    def __getitem__(self, filename):
        """Get the local or online version for this file.
        """
        vs = self._dict.get(filename)

        return datetime.strptime(vs, "%Y-%m-%d %H:%M:%S") if vs else None

    def __setitem__(self, filename, new_version):
        """Update the version value for this file.
        """
        self._dict[filename] = new_version.strftime("%Y-%m-%d %H:%M:%S")
        self._save()

    def _load(self):
        """Load the data file.
        """
        try:
            with open(Version._path) as f:
                data = json.load(f)
        except OSError:
            data = {}

        return data

    def _save(self):
        """Save the data file.
        """
        with open(Version._path, "w") as f:
            json.dump(self._dict, f)
