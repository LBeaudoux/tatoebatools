import logging

from .config import LINKS_DIR, SENTENCES_DIR
from .corpus import Corpus
from .datafile import DataFile
from .links import Links

DOWNLOAD_URL = "https://downloads.tatoeba.org/exports"


def update(*language_codes):
    """Update all data files required for these languages.
    """
    if update_sentences(*language_codes):
        update_links(*language_codes)

    logging.info(
        "data files up to date for {}".format(", ".join(language_codes))
    )


def update_sentences(*language_codes):
    """Update the sentences datafiles for these languahes.
    """
    lang_datafiles = [
        DataFile(
            f"{lg}_sentences_detailed.tsv",
            f"{DOWNLOAD_URL}/per_language/{lg}",
            SENTENCES_DIR,
        )
        for lg in language_codes
    ]
    return all(df.fetch() for df in lang_datafiles)


def update_links(*language_codes):
    """Update the links data file and split it by language pair for these 
    languages.
    """
    links_datafile = DataFile(
        "links.csv", DOWNLOAD_URL, LINKS_DIR, is_archived=True
    )
    if links_datafile.fetch():
        lg_pairs = [
            (lg1, lg2) for lg1 in language_codes for lg2 in language_codes
        ]
        links_versions = [Links(*pair).version for pair in lg_pairs]

        if not all(vs == links_datafile.version for vs in links_versions):
            logging.info("mapping sentences' ids to languages")
            lg_index = {
                str(s.id): s.lang for lg in language_codes for s in Corpus(lg)
            }
            links_datafile.split(lg_index, 0, 1)
