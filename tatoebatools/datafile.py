import csv
import logging
from pathlib import Path

from tqdm import tqdm

from .utils import (
    Buffer,
    decompress,
    download,
    extract,
    get_path_last_modified_datetime,
    get_url_last_modified_datetime,
)


class DataFile:
    """A parent class for handling data files.
    """

    def __init__(self, filename, endpoint, directory, is_archived=False):
        # the name of the datafile
        self._fn = filename
        # the endpoint url from which the datafile is downloadable
        self._ep = endpoint
        # the path of the directory where the datafile is downloaded
        self._dp = Path(directory)
        # if the datafile is archived
        self._ax = is_archived

    def fetch(self):
        """Download, decompress extract a datafile.
        """
        if not self.version or self.version < self.online_version:
            logging.info(f"downloading {self.bz2_name}")
            download(self.url, self.bz2_path)

        if not self.version or self.version < self.bz2_version:
            logging.info(f"decompressing {self.bz2_name}")
            decompress(self.bz2_path)

        if self.is_archived:
            logging.info(f"extracting {self.name}")
            extract(self.tar_path)

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
        return get_path_last_modified_datetime(self.path)

    @property
    def online_version(self):
        """Get the online version of a datafile.
        """
        return get_url_last_modified_datetime(self.url)

    @property
    def bz2_version(self):
        """Get the version of the local compressed file.
        """
        return get_path_last_modified_datetime(self.bz2_path)

    @property
    def size(self):
        """Get the byte size of the data file.
        """
        if self.path.is_file():
            return self.path.stat().st_size
        else:
            return 0


class LinksFile(DataFile):
    """The Tatoeba unique 'links.csv' data file.    
    """

    def __iter__(self):

        try:
            with open(self.path) as f:
                rows = csv.reader(f, delimiter="\t")
                for row in rows:
                    yield row
        except OSError:
            logging.exception(f"an error occurred while reading {self.path}")

    def classify(self, language_mapping):
        """Split the links.csv file by language pair.
        """
        logging.info("classifying translations by language")

        # init the progress bar
        pbar = tqdm(total=self.size, unit="iB", unit_scale=True)
        # init buffer
        buffer = Buffer(self.path.parent)
        # classify the rows
        for link in self:
            src_lg = language_mapping.get(int(link[0]))
            tgt_lg = language_mapping.get(int(link[1]))

            if src_lg and tgt_lg:
                fname = f"{src_lg}-{tgt_lg}_{self.name}"
                buffer.add(link, fname)

            # imcrement progress bar by the byte size of the row
            s = "\t".join(link) + "\n"
            pbar.update(len(s.encode("utf-8")))

        buffer.clear()
