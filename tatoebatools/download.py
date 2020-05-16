from .config import DATA_DIR
from .utils import fetch, get_filestem
from .version import Version


class Download:
    """A file download.
    """

    def __init__(self, url, version):
        # the url from which the file is downloaded
        self._url = url
        # the datetime used as the version of the file
        self._vs = version

    def fetch(self):
        """Download, decompress, extract, delete tamporary files, update
        local version value.
        """
        if fetch(self.from_url, self.out_dir):
            with Version() as local_versions:
                local_versions[self.stem] = self.version

            return self.table

        return

    @property
    def from_url(self):
        """Get the url from which the file is fetched.
        """
        return self._url

    @property
    def version(self):
        """Get the version of the downloaded file.
        """
        return self._vs

    @property
    def stem(self):
        """Get the stem of the downloaded file, e.g. 'foobar.txt' -> 'foobar'
        """
        return get_filestem(self.from_url)

    @property
    def table(self):
        """Get the name of the table from which this datafile is extracted.
        """
        stem = get_filestem(self.from_url)
        for tbl in ("sentences_detailed", "sentences_CC0", "transcriptions"):
            if stem.endswith(tbl):
                return tbl

        for tbl in (
            "links",
            "tags",
            "user_lists",
            "sentences_in_lists",
            "jpn_indices",
            "sentences_with_audio",
            "user_languages",
            "queries",
        ):
            if stem == tbl:
                return tbl

        return

    @property
    def out_dir(self):
        """Get the path of the directory into which the downloaded file is
        saved.
        """
        return DATA_DIR.joinpath(self.table)
