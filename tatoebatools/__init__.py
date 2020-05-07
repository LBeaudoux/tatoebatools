import logging

from .config import DATA_DIR
from .datafile import DataFile
from .sentences import Sentences

DOWNLOAD_URL = "https://downloads.tatoeba.org"


def update_corpus(*language_codes):
    """Update all data files required for these languages.
    """
    datafiles = get_monolingual_datafiles(
        "sentences_detailed.tsv", *language_codes
    )
    links_datafile = get_exports_datafile("links.csv")
    audios_datafile = get_exports_datafile("sentences_with_audio.csv")
    datafiles.extend([links_datafile, audios_datafile])

    if any(df.fetch() for df in datafiles):
        language_index = get_language_index(*language_codes)
        links_datafile.split(columns=[0, 1], index=language_index)
        audios_datafile.split(columns=[0], index=language_index)

    logging.info(
        "corpus data files up to date for {}".format(", ".join(language_codes))
    )


def update_stats():
    """Update all stats related datafiles.
    """
    queries_datafile = get_stats_datafile("queries.csv")
    print(queries_datafile.url)
    if queries_datafile.fetch():
        queries_datafile.split(columns=[1])

    logging.info("stats data files up to date")


def get_monolingual_datafiles(filename, *language_codes):
    """Get the sentences datafile instances for these languages.
    """
    return [
        DataFile(
            f"{lg}_{filename}",
            f"{DOWNLOAD_URL}/exports/per_language/{lg}",
            DATA_DIR.joinpath(filename.rsplit(".", 1)[0]),
        )
        for lg in language_codes
    ]


def get_exports_datafile(filename):
    """Get the datafile instance with this name from the exports url.
    """
    return DataFile(
        filename,
        f"{DOWNLOAD_URL}/exports",
        DATA_DIR.joinpath(filename.rsplit(".", 1)[0]),
        is_archived=True,
    )


def get_stats_datafile(filename):
    """Get the datafile instance with this name from the stats url.
    """
    return DataFile(
        filename,
        f"{DOWNLOAD_URL}/stats",
        DATA_DIR.joinpath(filename.rsplit(".", 1)[0]),
        is_archived=False,
        delimiter=",",
    )


def get_language_index(*language_codes):
    """Get the index that maps the sentences' ids to their language.
    """
    logging.info("mapping sentences' ids to languages")

    return {str(s.id): s.lang for lg in language_codes for s in Sentences(lg)}
