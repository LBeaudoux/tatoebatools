import csv
import logging
from pathlib import Path
from sys import getsizeof

from tqdm import tqdm

from .utils import (
    decompress,
    download,
    extract,
    get_url_last_modified_datetime,
    lazy_property,
)
from .version import Versions


class DataFile:
    """A parent class for handling data files.
    """

    def __init__(
        self, filename, endpoint, directory, is_archived=False, delimiter="\t"
    ):
        # the name of the datafile
        self._fn = filename
        # the endpoint url from which the datafile is downloadable
        self._ep = endpoint
        # the path of the directory where the datafile is downloaded
        self._dp = Path(directory)
        # if the datafile is archived
        self._ax = is_archived
        # the delimiter used in the csv file
        self._dm = delimiter

    def __iter__(self):

        try:
            with open(self.path) as f:
                reader = csv.reader(f, delimiter=self._dm)
                nb_cols = len(next(reader))
                f.seek(0) 
                for row in reader:
                    if len(row) == nb_cols:
                        yield row
        except OSError:
            logging.exception(f"an error occurred while reading {self.path}")

    def fetch(self):
        """Download, decompress extract a datafile.
        """
        new_version = self.online_version

        if self.version == new_version:
            return
        elif not self.version or self.version < self.online_version:
            if download(self.url, self.bz2_path) and decompress(self.bz2_path):
                self.bz2_path.unlink()
                if self.is_archived:
                    extract(self.tar_path)
                    self.tar_path.unlink()

                self.version = new_version

        return self.version

    def split(self, columns=[], index=None):
        """Split the file according to the values mapped by the index
        in a chosen set of columns. 
        """
        logging.info(f"splitting {self.name}")

        # init the progress bar
        pbar = tqdm(total=self.size, unit="iB", unit_scale=True)
        # init buffer
        buffer = Buffer(self.path.parent, delimiter=self._dm)
        # classify the rows
        for row in self:
            mapped_vals = [
                index.get(row[col]) if index else row[col]
                for col in columns
                if len(row) > col
            ]

            if all(mapped_vals):
                mapped_vals_string = "-".join(mapped_vals)
                fname = f"{mapped_vals_string}_{self.name}"
                buffer.add(row, fname)

            # imcrement progress bar by the byte size of the row
            line = self._dm.join(row) + "\n"
            pbar.update(len(line.encode("utf-8")))

        # update versions
        for fn in buffer.out_filenames:
            Versions().update(fn, self.version)

        buffer.clear()

        pbar.close()

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
        return Versions().get(self.name)

    @version.setter
    def version(self, new_version):
        """Set the local version of the datafile
        """
        Versions().update(self.name, new_version)

    @lazy_property
    def online_version(self):
        """Get the online version of a datafile.
        """
        print(self.url)

        return get_url_last_modified_datetime(self.url)

    @property
    def size(self):
        """Get the byte size of the data file.
        """
        if self.path.is_file():
            return self.path.stat().st_size
        else:
            return 0


class Buffer:
    """A buffer temporarily stores data and then appends it into out files 
    when full. It is useful to avoid memory overflow when handling very large 
    data files.
    """

    def __init__(self, out_dir, delimiter="\t", max_size=10000):
        # directory path where out files are saved.
        self._dir = Path(out_dir)
        # the feed delimiter used in the out files
        self._dm = delimiter
        # maximum number elements in a buffer
        self._max = max_size
        # the buffer data is classified in a dict. The dict keys are named
        # after the out filenames the data is directed to.
        self._data = {}

    def add(self, elt, out_fname):
        """Adds an element into the buffer linked to 'out_fname'. Once the 
        buffer is full, this element is appended to the file at 
        'out_dir/out_fname'.
        """
        if out_fname not in self._data:
            self._data[out_fname] = []
            # reinitialize the out file
            out_fp = Path(self._dir, out_fname)
            fpaths = {fp for fp in self._dir.iterdir()}
            if out_fp in fpaths:
                out_fp.unlink()

        self._data.setdefault(out_fname, []).append(elt)

        if getsizeof(self._data[out_fname]) > self._max:
            self._save(out_fname)

    def _save(self, out_fname, end=False):
        """Appends buffered elements into their out datafile and then clears
        the buffer.
        """
        data = self._data[out_fname]
        out_fp = Path(self._dir, f"{out_fname}.part")
        try:
            with open(out_fp, mode="a") as f:
                wt = csv.writer(f, delimiter=self._dm)
                wt.writerows(data)
        except OSError:
            logging.exception(f"an error occured when opening {out_fp}")
        else:
            self._data[out_fname].clear()

            if end:
                # removes '.part' extension
                out_fp.rename(out_fp.parent.joinpath(out_fp.stem))

    def clear(self):
        """Saves the data remaining in the buffer into the corresponding 
        outfiles.
        """
        for out_fname in self._data.keys():
            self._save(out_fname, end=True)

        self._data.clear()

    @property
    def out_filenames(self):
        """List every out file name.
        """
        return list(self._data.keys())
