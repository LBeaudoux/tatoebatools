import bz2
import logging
import tarfile
from datetime import datetime
from pathlib import Path

import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


def get_url_last_modified_datetime(file_url):
    """Get the last modified datetime of a file which is online.
    """
    try:
        with requests.get(file_url, stream=True) as r:
            dt_string = r.headers["last-modified"]
            dt = datetime.strptime(dt_string, "%a, %d %b %Y %H:%M:%S %Z")
    except Exception:
        logger.exception(
            f"did not get url last modified datetime of {file_url}"
        )
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


def download(from_url, to_directory):
    """Download a file. Overwrite previous version.
    """
    logger.info(f"downloading {from_url}")

    filename = from_url.rsplit("/", 1)[-1]
    to_dir_path = Path(to_directory)
    to_dir_path.mkdir(parents=True, exist_ok=True)
    to_path = to_dir_path.joinpath(filename)

    try:
        with requests.get(from_url, stream=True) as r:
            r.raise_for_status()
            # init progress bar
            total_size = int(r.headers.get("content-length", 0))
            tqdm_args = {
                "total": total_size,
                "unit": "iB",
                "unit_scale": True,
            }
            with tqdm(**tqdm_args) as pbar:
                with open(to_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                        pbar.update(len(chunk))  # update progress bar
    except requests.exceptions.RequestException:
        logger.info(f"downloading of {from_url} failed")
        return
    else:
        return to_path


def decompress(compressed_path):
    """Decompress a bz2 file here. Overwrite previous version.
    """
    in_path = Path(compressed_path)
    out_path = in_path.parent.joinpath(in_path.stem)

    logger.debug(f"decompressing {in_path.name}")

    try:
        with bz2.open(in_path) as in_f:
            with open(out_path, "wb") as out_f:
                data = in_f.read()
                out_f.write(data)
    except Exception:
        logger.exception(f"error while decompressing {compressed_path}")
        return
    else:
        return out_path


def extract(archive_path):
    """Extract here all files in an archive. Overwrite previous versions.
    """
    arx_path = Path(archive_path)

    logger.debug(f"extracting {arx_path.name}")

    try:
        with tarfile.open(arx_path) as tar:
            tar.extractall(arx_path.parent)
            extracted_filenames = tar.getnames()
    except tarfile.ReadError:
        logger.exception(f"{arx_path} is not extractable")
        return []
    else:
        return [arx_path.parent.joinpath(fn) for fn in extracted_filenames]


def fetch(from_url, to_directory):
    """Download a file, decompress it, extract it and delete temporary files.
    Overwrite previous versions.
    """
    dl_path = download(from_url, to_directory)

    if not dl_path:
        return []
    elif str(dl_path).endswith(".bz2"):
        uz_path = decompress(dl_path)
        dl_path.unlink()
        if str(uz_path).endswith(".tar"):
            out_paths = extract(uz_path)
            uz_path.unlink()
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
    """Get the stem of the file at this url.
    """
    return url.rsplit("/", 1)[-1].split(".", 1)[0]


def get_endpoint(url):
    """Get the parent url of this url.
    """
    return url.rsplit("/", 1)[0]


def get_byte_size_of_row(row, delimiter):
    """Get the byte size of this row split by this delimiter.
    """
    line = delimiter.join(row) + "\n"

    return len(line.encode("utf-8"))
