import csv
import logging
from pathlib import Path
from sys import getsizeof

logger = logging.getLogger(__name__)


class Buffer:
    """A buffer temporarily stores data and then appends it into out files
    when full. It is useful to avoid memory overflow when handling very large
    data files.
    """

    def __init__(self, out_dir, delimiter="\t", max_size=10000):
        # directory path where out files are saved.
        self._dir = Path(out_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._fps = set(self._dir.iterdir())  # files already in the out_dir
        # the feed delimiter used in the out files
        self._dm = delimiter
        # maximum number elements in a buffer
        self._max = max_size
        # the buffer data is classified in a dict. The dict keys are named
        # after the out filenames the data is directed to.
        self._data = {}

    def __getitem__(self, out_fname):

        return self._data[out_fname]

    def __setitem__(self, out_fname, data):

        self._data[out_fname] = data

    def __len__(self):

        return len(self._data)

    def add(self, elt, out_fname):
        """Adds an element into the buffer linked to 'out_fname'. Once the
        buffer is full, this element is appended to the file at
        'out_dir/out_fname'.
        """
        if out_fname not in self._data:
            self._data[out_fname] = []
            # reinitialize the out file
            out_fp = Path(self._dir, out_fname)
            if out_fp in self._fps:
                out_fp.unlink()
                self._fps.remove(out_fp)

        self._data.setdefault(out_fname, []).append(elt)

        if getsizeof(self._data[out_fname]) > self._max:
            self._save(out_fname)

    def _save(self, out_fname, end=False):
        """Appends buffered elements into their out datafile and then clears
        the buffer.
        """
        data = list(self._data[out_fname])
        out_fp = Path(self._dir, f"{out_fname}.part")
        try:
            with open(out_fp, mode="a") as f:
                wt = csv.writer(f, delimiter=self._dm)
                wt.writerows(data)
        except FileNotFoundError:
            logger.debug(f"an error occured when opening {out_fp}")
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
    def directory(self):
        """Get the path of the directory where the buffer files are saved."""
        return self._dir

    @property
    def out_filenames(self):
        """List every out file name."""
        return list(self._data.keys())
