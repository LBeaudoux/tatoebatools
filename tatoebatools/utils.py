import bz2
import csv
import logging
import tarfile
from datetime import datetime
from pathlib import Path
from sys import getsizeof

import requests
from tqdm import tqdm


class Buffer:
    """A buffer temporarily stores data and then appends it into out files 
    when full. It is useful to avoid memory overflow when handling very large 
    data files.
    """

    def __init__(self, out_dir, max_size=1000):
        # directory path where out files are saved.
        self._dir = Path(out_dir)
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
                wt = csv.writer(f, delimiter="\t")
                wt.writerows(data)
        except OSError:
            logging.exception()
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


def get_url_last_modified_datetime(file_url):
    """Get the last modified datetime of a file which is online.
    """
    try:
        with requests.get(file_url, stream=True) as r:
            dt_string = r.headers["last-modified"]
            dt = datetime.strptime(dt_string, "%a, %d %B %Y %H:%M:%S %Z")
    except Exception:
        return
    else:
        return dt


def get_path_last_modified_datetime(file_path):
    """Get the last modified datetime of a local file.
    """
    try:
        fp = Path(file_path)
        dt = datetime.fromtimestamp(fp.stat().st_mtime)
    except FileNotFoundError:
        return
    else:
        return dt


def download(from_url, to_path, chunk_size=1024):
    """Download a file.
    """
    try:
        with requests.get(from_url, stream=True) as r:
            r.raise_for_status()
            # init progress bar
            total_size = int(r.headers.get("content-length", 0))
            tqdm_args = {"total": total_size, "unit": "iB", "unit_scale": True}
            with tqdm(**tqdm_args) as pbar:
                with open(to_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        pbar.update(len(chunk))  # update progress bar
    except Exception:
        logging.exception(f"error while downloading {from_url} to {to_path}")


def decompress(compressed_path):
    """Decompress here a bz2 file.
    """
    in_path = Path(compressed_path)
    out_path = in_path.parent.joinpath(in_path.stem)

    try:
        with bz2.open(in_path) as in_f:
            with open(out_path, "wb") as out_f:
                data = in_f.read()
                out_f.write(data)
    except Exception as e:
        print(e)


def extract(archive_path):
    """Extract here all files in an archive.
    """
    arx_path = Path(archive_path)
    try:
        with tarfile.open(arx_path) as tar:
            tar.extractall(arx_path.parent)
    except tarfile.ReadError:
        logging.exception(f"{arx_path} is not extractable")
