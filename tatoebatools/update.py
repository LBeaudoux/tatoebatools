import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .utils import get_endpoint, get_filestem
from .version import version

logger = logging.getLogger(__name__)


def check_updates(tables, languages, verbose=True):
    """Check for updates on 'downloads.tatoeba.org' for these tables and these
    languages.
    """
    if verbose:
        logger.info("checking for updates on https://downloads.tatoeba.org")

    # get the urls where newer versions of datafiles could be found
    urls_to_check = _get_urls_to_check(tables, languages)
    # get the urls of the web pages from which file versions will be scraped
    urls_to_scrap = {get_endpoint(url) for url in urls_to_check}

    to_update = {}
    pbar = tqdm(total=len(urls_to_scrap)) if verbose else None
    for url in urls_to_scrap:
        online_versions = _scrap_versions(url)
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

    return to_update


def _get_urls_to_check(tables, languages):
    """Get the urls where datafiles may be downloadable for these tables 
    and languages.
    """
    ROOT_URL = "https://downloads.tatoeba.org"

    urls = set()
    for tbl in tables:
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
                    for lg in languages
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
            urls.update(
                [
                    f"{ROOT_URL}/exports/per_language/{lg1}/{lg1}-{lg2}_{tbl}.tsv.bz2"
                    for lg1 in languages
                    for lg2 in languages
                ]
            )
        elif tbl == "queries":
            urls.add(f"{ROOT_URL}/stats/{tbl}.csv.bz2")

    return urls


def _scrap_versions(url):
    """Scrap the versions of the files downloadable from a 
    'downloads.tatoeba.org' web page.
    """
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        return
    else:
        soup = BeautifulSoup(r.text, features="html.parser").find("pre")

        texts = [x.strip() for x in soup.findAll(text=True)]

        return {
            f"{url}/{x}": datetime.strptime(
                texts[i + 1][:17], "%d-%b-%Y %H:%M"
            )
            for i, x in enumerate(texts)
            if i % 2 == 0 and texts[i + 1] and x[-1] != "/"
        }
