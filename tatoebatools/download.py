from pathlib import Path

from .utils import (
    decompress,
    download,
    extract,
    get_url_last_modified_datetime,
    lazy_property,
)

from .version import Version


class Download:
    """
    """

    def __init__(self, filename, endpoint, directory, is_archived=False):
        # the name of the datafile
        self._fn = filename
        # the endpoint url from which the datafile is downloadable
        self._ep = endpoint
        # the path of the directory where the datafile is downloaded
        self._dp = Path(directory)
        self._dp.mkdir(parents=True, exist_ok=True)
        # if the datafile is archived
        self._ax = is_archived

    def fetch(self):
        """Download, decompress extract a datafile.
        """
        if self.is_up_to_date:
            pass
        elif download(self.url, self.bz2_path) and decompress(self.bz2_path):
            self.bz2_path.unlink()
            if self.is_archived:
                extract(self.tar_path)
                self.tar_path.unlink()

            self.version = self.online_version

            return self.version

        return

    @property
    def name(self):
        """Get the name of this datafile.
        """
        return self._fn

    @property
    def endpoint_url(self):
        """Get the endpoint from which this datafile is downloaded.
        """
        return self._ep

    @property
    def path(self):
        """Get the path of this datafile.
        """
        return self._dp.joinpath(self._fn)

    @property
    def is_archived(self):
        """Check if the datafile is archived.
        """
        return self._ax

    @property
    def tar_name(self):
        """Get the name of the archive of the datafile.
        """
        return f"{self.path.stem}.tar"

    @property
    def tar_path(self):
        """Get the name of the archive of the datafile.
        """
        return self._dp.joinpath(self.tar_name)

    @property
    def bz2_name(self):
        """Get the name of the compressed version of this datafile.
        """
        fn = self.tar_name if self.is_archived else self.name

        return f"{fn}.bz2"

    @property
    def bz2_path(self):
        """Get the path of the compressed version of this datafile.
        """
        return self._dp.joinpath(self.bz2_name)

    @property
    def url(self):
        """Get the url from which this datafile is downloaded.
        """
        return f"{self._ep}/{self.bz2_name}"

    @property
    def version(self):
        """Get the local version of the datafile.
        """
        return Version()[self.name]

    @version.setter
    def version(self, new_version):
        """Set the local version of the datafile
        """
        Version()[self.name] = new_version

    @lazy_property
    def online_version(self):
        """Get the online version of a datafile.
        """
        return get_url_last_modified_datetime(self.url)

    @property
    def is_up_to_date(self):
        """Check if this download is already done.
        """
        return self.version and self.version == self.online_version

    @property
    def size(self):
        """Get the byte size of the data file.
        """
        if self.path.is_file():
            return self.path.stat().st_size
        else:
            return 0
