from .config import DATA_DIR
from .utils import fetch, get_filestem
from .version import version


class Download:
    """A file download."""

    def __init__(self, url, version):
        # the url from which the file is downloaded
        self._url = url
        # the datetime used as the version of the file
        self._vs = version

    def fetch(self):
        """Download, decompress, extract, delete tamporary files, update
        local version value.
        """
        fetched = fetch(self.from_url, self.out_dir)
        if fetched:
            version[self.stem] = self.version

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
    def stem(self):
        """Get the stem of the downloaded file
        'https://foo.bar/foobar.txt' -> 'foobar'
        """
        return get_filestem(self.from_url)

    @property
    def table(self):
        """Get the name of the table from which this datafile is extracted."""
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
            if self.stem.endswith(tbl):
                return tbl

        for tbl in (
            "user_lists",
            "jpn_indices",
            "queries",
        ):
            if self.stem == tbl:
                return tbl

        return

    @property
    def out_dir(self):
        """Get the path of the directory into which the downloaded file is
        saved.
        """
        return DATA_DIR.joinpath(self.table)
