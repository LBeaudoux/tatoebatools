import logging
from pathlib import Path

from .config import (
    DATA_DIR,
    DIFFERENCE_TABLES,
    SUPPORTED_TABLES,
    TABLE_CSV_PARAMS,
)
from .datafile import DataFile
from .download import Download
from .download_page import download_pages
from .exceptions import NotLanguagePair
from .utils import get_endpoint, get_filestem
from .version import version

logger = logging.getLogger(__name__)


class Update:
    """A handler for updating data files"""

    def __init__(self, table_language_pairs, data_dir=None):
        """
        Parameters
        ----------
        table_language_pairs : list of tuples
            table name / language codes pairs
        data_dir : str, optional
            the directory where the data is stored,
            set to None to use the config default data directory
        """
        self._tlps = table_language_pairs
        self._data_dir = Path(data_dir) if data_dir else DATA_DIR

    def run(self, verbose=True):
        """Run the update"""
        self._vb = verbose
        to_download = self._check()
        downloads = self._download(to_download)
        new_datafiles = self._split(downloads)
        self._find_changes(new_datafiles)

    def _check(self):
        """Get the urls and versions of the datafiles for which a newer
        version is available online
        """
        to_download = {}
        for tbl, lgs in self._tlps:
            langs = ["*"] if (not lgs or "*" in lgs) else lgs
            d = check_updates(
                [tbl], langs, oriented_pair=True, verbose=self._vb
            )
            to_download.setdefault(tbl, {}).update(d)

        return to_download

    def _download(self, to_download):
        """Download the files to update"""
        downloads = {}
        for tbl, d in to_download.items():
            for url, vs in d.items():
                dl = Download(url, vs, data_dir=self._data_dir)
                dl_paths = dl.fetch(verbose=self._vb)
                downloads.setdefault(tbl, []).extend(dl_paths)

        return downloads

    def _split(self, downloads):
        """Split datafiles not 'monolingually' available"""
        new_dfiles = {}
        for tbl, fps in downloads.items():
            tbl_params = TABLE_CSV_PARAMS[tbl]
            for fp in fps:
                dfile = DataFile(fp, **tbl_params)
                tbl_dfiles = {dfile}
                if dfile.path.stem == "queries":
                    splits = dfile.split(
                        columns=[1], verbose=self._vb, save=True
                    )
                    tbl_dfiles |= set(splits)
            new_dfiles[tbl] = tbl_dfiles

        return new_dfiles

    def _find_changes(self, new_datafiles):
        """Compare new datafiles with their older version"""
        for tbl, dfiles in new_datafiles.items():
            for dfile in dfiles:
                if any(t in dfile.path.stem for t in DIFFERENCE_TABLES):
                    dfile.find_changes(save=True, verbose=self._vb)


def check_languages():
    """Lists all available languages for Tatoeba downloads"""
    url = "https://downloads.tatoeba.org/exports/per_language"

    return download_pages.get_names(url)


def check_tables():
    """Lists all available tables for Tatoeba downloads"""
    return sorted(list(SUPPORTED_TABLES))


def check_updates(
    table_names,
    language_codes,
    oriented_pair=False,
    verbose=True,
):
    """Check for updates on for these tables and these languages"""
    # get the urls where newer versions of datafiles could be found
    urls_to_check = _get_urls_to_check(
        table_names, language_codes, oriented_pair
    )
    # get the urls of the web pages from which file versions will be scraped
    urls_to_scrap = {get_endpoint(url) for url in urls_to_check}

    to_update = {}
    for url in urls_to_scrap:
        online_versions = download_pages.get_versions(url)
        # compare versions
        for url, vs in online_versions.items():
            if url in urls_to_check:
                current_vs = version[get_filestem(url)]
                if not current_vs or current_vs.date() < vs.date():
                    to_update[url] = vs

    return to_update


def _get_urls_to_check(table_names, language_codes, oriented_pair):
    """Get the urls where datafiles may be downloadable for these tables
    and languages.
    """
    ROOT_URL = "https://downloads.tatoeba.org"

    urls = set()
    for tbl in table_names:
        if tbl in (
            "sentences_base",
            "sentences_CC0",
            "sentences_detailed",
            "sentences_in_lists",
            "sentences_with_audio",
            "tags",
            "transcriptions",
            "user_languages",
        ):
            if language_codes == ["*"]:
                urls.add(f"{ROOT_URL}/exports/{tbl}.tar.bz2")
            else:
                urls.update(
                    [
                        f"{ROOT_URL}/exports/per_language/{lg}/"
                        f"{lg}_{tbl}.tsv.bz2"
                        for lg in language_codes
                    ]
                )
        elif tbl in {
            "jpn_indices",
            "user_lists",
        }:
            urls.add(f"{ROOT_URL}/exports/{tbl}.tar.bz2")
        elif tbl in {
            "links",
        }:
            if language_codes == ["*"]:
                urls.add(f"{ROOT_URL}/exports/{tbl}.tar.bz2")
            elif oriented_pair:
                if len(language_codes) != 2:
                    raise NotLanguagePair(language_codes)
                else:
                    lg1 = language_codes[0]
                    lg2 = language_codes[1]
                    urls.add(
                        f"{ROOT_URL}/exports/per_language/{lg1}/"
                        f"{lg1}-{lg2}_{tbl}.tsv.bz2"
                    )
            else:
                urls.update(
                    [
                        f"{ROOT_URL}/exports/per_language/{lg1}/"
                        f"{lg1}-{lg2}_{tbl}.tsv.bz2"
                        for lg1 in language_codes
                        for lg2 in language_codes
                    ]
                )
        elif tbl == "queries":
            urls.add(f"{ROOT_URL}/stats/{tbl}.csv.bz2")

    return urls
