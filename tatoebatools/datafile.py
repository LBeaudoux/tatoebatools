import csv
import logging
from pathlib import Path
from sys import getsizeof

from tqdm import tqdm


from .version import Version


class DataFile:
    """A file containing table data.
    """

    def __init__(self, file_path, delimiter="\t"):
        # the local path of this data file
        self._fp = Path(file_path)
        # the delimiter that distinguishes table columns
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
            logging.debug(f"an error occurred while reading {self.path}")

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
            Version()[fn] = self.version

        buffer.clear()

        pbar.close()

    @property
    def path(self):
        """Get the path of this datafile.
        """
        return self._fp

    @property
    def name(self):
        """Get the name of this datafile.
        """
        return self._fp.name

    @property
    def version(self):
        """Get the local version of this datafile.
        """
        return Version()[self.name]

    @property
    def size(self):
        """Get the byte size of this data file.
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
        self._dir.mkdir(parents=True, exist_ok=True)
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
