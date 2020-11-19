from pathlib import Path

from .config import DATA_DIR
from .utils import fetch, get_filestem
from .version import version


class Download:
    """A file download"""

    def __init__(self, url, version, data_dir=None):
        """
        Parameters
        ----------
        url : str
            the url from which the file is downloaded
        version : datetime
            the version of the file
        data_dir :  str, optional
            the parent directory where files are downloaded, by default None
        """
        self._url = url
        self._vs = version
        self._data_dir = Path(data_dir) if data_dir else DATA_DIR

    def fetch(self, verbose=True):
        """Download, decompress, extract, delete tamporary files, update
        local version value.
        """
        fetched = fetch(self._url, self.out_dir, verbose=verbose)
        if fetched:
            version[self.name] = self._vs

        return fetched

    @property
    def from_url(self):
        """Get the url from which the file is fetched."""
        return self._url

    @property
    def version(self):
        """Get the version of the downloaded file."""
        return self._vs

    @property
    def name(self):
        """Get the name of the download
        'https://foo.bar/foobar.txt' -> 'foobar'
        """
        return get_filestem(self.from_url)

    @property
    def table(self):
        """Get the name of the table from which this datafile is extracted"""
        for tbl in (
            "sentences_base",
            "sentences_detailed",
            "sentences_CC0",
            "transcriptions",
            "links",
            "tags",
            "sentences_in_lists",
            "sentences_with_audio",
            "user_languages",
        ):
            if self.name.endswith(tbl):
                return tbl

        for tbl in (
            "user_lists",
            "jpn_indices",
            "queries",
        ):
            if self.name == tbl:
                return tbl

        return

    @property
    def out_dir(self):
        """Get the path of the directory into which the downloaded file is
        saved.
        """
        return self._data_dir.joinpath(self.table)
