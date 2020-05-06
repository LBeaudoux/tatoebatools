import logging

from .config import LINKS_DIR, SENTENCES_DIR
from .corpus import Corpus
from .datafile import DataFile

DOWNLOAD_URL = "https://downloads.tatoeba.org/exports"


def update(*language_codes):
    """Update all data files required for these languages.
    """
    lang_datafiles = [
        DataFile(
            f"{lg}_sentences_detailed.tsv",
            f"{DOWNLOAD_URL}/per_language/{lg}",
            SENTENCES_DIR,
        )
        for lg in language_codes
    ]

    if all(df.fetch() for df in lang_datafiles):
        links_datafile = DataFile(
            "links.csv", DOWNLOAD_URL, LINKS_DIR, is_archived=True
        )
        if links_datafile.fetch():
            logging.info("mapping sentences' ids to languages")
            lg_index = {
                str(s.id): s.lang for lg in language_codes for s in Corpus(lg)
            }
            links_datafile.split(lg_index, 0, 1)

    logging.info("data updated for {}".format(", ".join(language_codes)))
