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
    """A file download.
    """

    def __init__(self, filename, endpoint, directory, is_archived=False):
        # the name of the file
        self._fn = filename
        # the endpoint url from which the file is downloadable
        self._ep = endpoint
        # the path of the directory where the file is downloaded
        self._dp = Path(directory)
        self._dp.mkdir(parents=True, exist_ok=True)
        # if the file is archived
        self._ax = is_archived

    def fetch(self):
        """Execute the download. Decompress and extract the downloaded file.
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
        """Get the name of the file to download.
        """
        return self._fn

    @property
    def endpoint_url(self):
        """Get the endpoint from which the file is downloaded.
        """
        return self._ep

    @property
    def path(self):
        """Get the local path where the file is saved.
        """
        return self._dp.joinpath(self._fn)

    @property
    def is_archived(self):
        """Check if the file is archived.
        """
        return self._ax

    @property
    def tar_name(self):
        """Get the name of the archive of the file.
        """
        return f"{self.path.stem}.tar"

    @property
    def tar_path(self):
        """Get the name of the archive of the file.
        """
        return self._dp.joinpath(self.tar_name)

    @property
    def bz2_name(self):
        """Get the name of the compressed version of the file.
        """
        fn = self.tar_name if self.is_archived else self.name

        return f"{fn}.bz2"

    @property
    def bz2_path(self):
        """Get the path of the compressed version of the file.
        """
        return self._dp.joinpath(self.bz2_name)

    @property
    def url(self):
        """Get the url from which the file is downloaded.
        """
        return f"{self._ep}/{self.bz2_name}"

    @property
    def version(self):
        """Get the local version of the file.
        """
        with Version() as vs:
            return vs[self.filename]

    @version.setter
    def version(self, new_version):
        """Set the local version of the file
        """
        with Version() as vs:
            vs[self.name] = new_version

    @lazy_property
    def online_version(self):
        """Get the online version of the file.
        """
        return get_url_last_modified_datetime(self.url)

    @property
    def is_up_to_date(self):
        """Check if this download is already done.
        """
        return self.version and self.version == self.online_version
