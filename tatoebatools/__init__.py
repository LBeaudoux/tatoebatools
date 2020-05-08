import logging

from .config import DATA_DIR
from .datafile import DataFile
from .sentences import Sentences

DOWNLOAD_URL = "https://downloads.tatoeba.org"


def update_corpus(*language_codes):
    """Update corpus-related data and classify it by language.
    The following data files are downloaded from downloads.tatoeba.org:
    - '<lang>_sentences_detailed.tsv'
    - 'links.csv'
    - 'sentences_with_audio.csv'
    """
    datafiles = [
        get_monolingual_datafile("sentences_detailed.tsv", lg)
        for lg in language_codes
    ]
    links_datafile = get_exports_datafile("links.csv")
    audios_datafile = get_exports_datafile("sentences_with_audio.csv")
    datafiles.extend([links_datafile, audios_datafile])

    if any(df.fetch() for df in datafiles):
        # split multilingual files by language for efficient access
        language_index = get_language_index(*language_codes)
        links_datafile.split(columns=[0, 1], index=language_index)
        audios_datafile.split(columns=[0], index=language_index)

    lg_string = ", ".join(language_codes)
    logging.info(f"corpus data files up to date for {lg_string}")


def update_stats(self):
    """Update statistics-related data and classify it by language.
    """
    queries_datafile = get_stats_datafile("queries.csv")
    if queries_datafile.fetch():
        # split multilingual file by language for efficient access
        queries_datafile.split(columns=[1])

    logging.info("stats data files up to date")


def get_monolingual_datafile(filename, language_code):
    """Get the sentences datafile instance for this languages.
    """
    return DataFile(
        f"{language_code}_{filename}",
        f"{DOWNLOAD_URL}/exports/per_language/{language_code}",
        DATA_DIR.joinpath(filename.rsplit(".", 1)[0]),
    )


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
