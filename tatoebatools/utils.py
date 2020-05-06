import bz2
import logging
import tarfile
from datetime import datetime
from pathlib import Path

import requests
from tqdm import tqdm


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
    logging.info(f"downloading {from_url}")

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
        return False
    else:
        return True


def decompress(compressed_path):
    """Decompress here a bz2 file.
    """
    in_path = Path(compressed_path)
    out_path = in_path.parent.joinpath(in_path.stem)

    logging.debug(f"decompressing {in_path.name}")

    try:
        with bz2.open(in_path) as in_f:
            with open(out_path, "wb") as out_f:
                data = in_f.read()
                out_f.write(data)
    except Exception:
        logging.exception(f"error while decompressing {compressed_path}")
        return False
    else:
        return True


def extract(archive_path):
    """Extract here all files in an archive.
    """
    arx_path = Path(archive_path)

    logging.debug(f"extracting {arx_path.name}")

    try:
        with tarfile.open(arx_path) as tar:
            tar.extractall(arx_path.parent)
    except tarfile.ReadError:
        logging.exception(f"{arx_path} is not extractable")
