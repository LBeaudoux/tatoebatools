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
        # the dict from which versions' values are fetched
        self._dict = self._load()
        # a boolean that indicates if the data has been modified since the 
        # last file loading
        self._save = False

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        
        if self._save:
            self.save()

    def __getitem__(self, filename):
        """Get the local or online version for this file.
        """
        vs = self._dict.get(filename)

        return datetime.strptime(vs, "%Y-%m-%d %H:%M:%S") if vs else None

    def __setitem__(self, filename, new_version):
        """Update the version value for this file.
        """
        self._dict[filename] = new_version.strftime("%Y-%m-%d %H:%M:%S")
        self._save = True

    def _load(self):
        """Load the data file.
        """
        try:
            with open(Version._path) as f:
                data = json.load(f)
        except OSError:
            data = {}

        return data

    def save(self):
        """Save the data file.
        """
        with open(Version._path, "w") as f:
            json.dump(self._dict, f)
