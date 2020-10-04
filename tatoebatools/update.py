import logging

from tqdm import tqdm

from .config import SUPPORTED_TABLES
from .download_page import DownloadPages
from .exceptions import NotLanguagePair
from .utils import get_endpoint, get_filestem
from .version import version

logger = logging.getLogger(__name__)


def check_languages():
    """Lists all available languages for Tatoeba downloads"""
    url = "https://downloads.tatoeba.org/exports/per_language"

    return DownloadPages().get_names(url)


def check_tables():
    """Lists all available tables for Tatoeba downloads"""

    return sorted(list(SUPPORTED_TABLES))


def check_updates(
    table_names, language_codes, oriented_pair=False, verbose=True
):
    """Check for updates on for these tables and these languages"""
    if verbose:
        msgs = [
            ", ".join([f"'{x}'" for x in a])
            for a in (table_names, language_codes)
        ]
        msg = f"checking updates for {msgs[0]}"
        if msgs[1]:
            msg += f" in {msgs[1]}"
        logger.info(msg)

    # get the urls where newer versions of datafiles could be found
    urls_to_check = _get_urls_to_check(
        table_names, language_codes, oriented_pair
    )
    # get the urls of the web pages from which file versions will be scraped
    urls_to_scrap = {get_endpoint(url) for url in urls_to_check}

    to_update = {}
    nb_scraps = len(urls_to_scrap)
    pbar = tqdm(total=nb_scraps) if verbose and nb_scraps >= 10 else None
    for url in urls_to_scrap:
        online_versions = DownloadPages().get_versions(url)
        # compare versions
        for url, vs in online_versions.items():
            if url in urls_to_check:
                current_vs = version[get_filestem(url)]
                if not current_vs or current_vs.date() < vs.date():
                    to_update[url] = vs

        if pbar:
            pbar.update()

    if pbar:
        pbar.close()

    if verbose:
        if to_update:
            logger.info(f"{len(to_update)} files to download")
        else:
            logger.info("files already up to date")

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
            urls.update(
                [
                    f"{ROOT_URL}/exports/per_language/{lg}/{lg}_{tbl}.tsv.bz2"
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
            if oriented_pair:
                if len(language_codes) != 2:
                    raise NotLanguagePair(language_codes)

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
