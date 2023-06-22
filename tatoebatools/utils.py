import bz2
import csv
import logging
import math
import os
import tarfile
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


def download(from_url, to_directory, verbose=True):
    """Download a file. Overwrite previous version."""
    # build out file path
    filename = from_url.rsplit("/", 1)[-1]
    to_dir_path = Path(to_directory)
    to_dir_path.mkdir(parents=True, exist_ok=True)
    to_path = to_dir_path.joinpath(filename)

    try:
        with requests.get(from_url, stream=True) as r:
            r.raise_for_status()
            # init progress bar
            if verbose:
                total_size = int(r.headers.get("content-length", 0))
                tqdm_args = {
                    "total": total_size,
                    "unit": "iB",
                    "unit_scale": True,
                }
                pbar = tqdm(**tqdm_args)
            else:
                pbar = None
            # write data in out file
            with open(to_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                if pbar:
                    pbar.close()
    except requests.exceptions.RequestException:
        logger.error(f"downloading of {from_url} failed")
        return
    else:
        return to_path


def decompress(compressed_path):
    """Decompress a bz2 file here. Overwrite previous version. Delete
    compressed file after decompression.
    """
    in_path = Path(compressed_path)
    out_path = in_path.parent.joinpath(in_path.stem)

    # rename latest decompressed file at this path (enables file comparison)
    indicate_as_old(out_path)

    try:
        with bz2.open(in_path) as in_f:
            with open(out_path, "wb") as out_f:
                data = in_f.read()
                out_f.write(data)
        in_path.unlink()
    except FileNotFoundError:
        logger.error(f"{compressed_path} not found by file decompressor")
        return
    except OSError:
        logger.error(f"{compressed_path} is not a valid compressed file")
        return
    else:
        return out_path


def extract(archive_path):
    """Extract here all files in an archive. Overwrite previous versions.
    Delete archive after extraction.
    """
    arx_path = Path(archive_path)

    try:
        with tarfile.open(arx_path) as tar:
            out_filenames = tar.getnames()
            out_paths = [arx_path.parent.joinpath(fn) for fn in out_filenames]
            # rename latest extracted files at this path for file comparison
            for fp in out_paths:
                indicate_as_old(fp)

            def is_within_directory(directory, target):
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)

                prefix = os.path.commonprefix([abs_directory, abs_target])

                return prefix == abs_directory

            def safe_extract(
                tar, path=".", members=None, *, numeric_owner=False
            ):
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")

                tar.extractall(path, members, numeric_owner=numeric_owner)

            safe_extract(tar, arx_path.parent)

        arx_path.unlink()
    except FileNotFoundError:
        logger.error(f"{arx_path} not found by file extractor")
        return []
    except tarfile.ReadError:
        logger.error(f"{arx_path} is not an extractable archive")
        return []
    else:
        return out_paths


def fetch(from_url, to_directory, verbose=True):
    """Download a file, decompress it, extract it and delete temporary files.
    Overwrite previous versions.
    """
    if verbose:
        logger.info(f"downloading {from_url}")
    dl_path = download(from_url, to_directory, verbose=verbose)

    if not dl_path:
        return []
    elif str(dl_path).endswith(".bz2"):
        if verbose:
            logger.info(f"decompressing {dl_path.name}")
        uz_path = decompress(dl_path)
        if str(uz_path).endswith(".tar"):
            if verbose:
                logger.info(f"extracting {uz_path.name}")
            out_paths = extract(uz_path)
            return out_paths
        else:
            return [uz_path]
    else:
        return [dl_path]


class lazy_property(object):
    """Implements a lazy property decorator. Lazy attributes are computed
    attributes that are evaluated only once, the first time they are used.
    Subsequent uses return the results of the first call.
    """

    def __init__(self, f):
        self.f = f
        self.name = f.__name__

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        val = self.f(instance)
        setattr(instance, self.name, val)

        return val


def get_filestem(url):
    """Get the stem of the file at this url."""
    return url.rsplit("/", 1)[-1].split(".", 1)[0]


def get_endpoint(url):
    """Get the parent url of this url."""
    return url.rsplit("/", 1)[0]


def get_byte_size(row, delimiter, line_terminator):
    """Get the byte size of this row split by this delimiter."""
    line = delimiter.join(row) + line_terminator

    return len(line.encode("utf-8"))


def get_extended_name(file_path, extension):
    """Appends the name of this file"""
    return f"{file_path.stem}_{extension}{file_path.suffix}"


def indicate_as_old(file_path):
    """Show that a file is an old version by including 'old' in its name
    'foobar.txt' -> 'foobar_old.txt'
    """
    if file_path.is_file():
        name_of_old = get_extended_name(file_path, "old")
        file_path.replace(file_path.with_name(name_of_old))


def count_csv_columns(csv_path, delimiter):
    """Count the columns in a CSV file"""
    nb_cols = None
    try:
        with open(csv_path, encoding="utf-8") as f:
            rd = csv.reader(f, delimiter=delimiter)
            nb_cols = len(next(rd))
    except FileNotFoundError:
        logger.exception("csv file not found")
    finally:
        return nb_cols


def list_attributes(any_class):
    """List all public methods and attributes of a class sorted by
    definition order
    """
    return [x for x in any_class.__dict__.keys() if not x.startswith("_")]


def is_na(element):
    """Check if an element is 'not available'"""
    if isinstance(element, str):
        return element == "N"
    elif isinstance(element, float):
        return math.isnan(element)
    return False


def parse_export_date(datetime_string):
    """Parse a datetime string from a weekly export file"""
    return pd.to_datetime(
        datetime_string, format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )


def parse_search_log_date(date_string):
    """Parse a date string from the search log file"""
    return pd.to_datetime(date_string, format="%d %b %Y", errors="coerce")
