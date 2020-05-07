import logging

from .config import DATA_DIR
from .datafile import DataFile
from .sentences import Sentences

DOWNLOAD_URL = "https://downloads.tatoeba.org/exports"


def update(*language_codes):
    """Update all data files required for these languages.
    """
    datafiles = get_monolingual_datafiles(
        "sentences_detailed.tsv", *language_codes
    )
    links_datafile = get_multilingual_datafile("links.csv")
    audios_datafile = get_multilingual_datafile("sentences_with_audio.csv")
    datafiles.extend([links_datafile, audios_datafile])

    if any(df.fetch() for df in datafiles):
        language_index = get_language_index(*language_codes)
        links_datafile.split(language_index, 0, 1)
        audios_datafile.split(language_index, 0)

    logging.info(
        "data files up to date for {}".format(", ".join(language_codes))
    )


def get_monolingual_datafiles(filename, *language_codes):
    """Get the sentences datafile instances for these languages.
    """
    return [
        DataFile(
            f"{lg}_{filename}",
            f"{DOWNLOAD_URL}/per_language/{lg}",
            DATA_DIR.joinpath(filename.rsplit(".", 1)[0]),
        )
        for lg in language_codes
    ]


def get_multilingual_datafile(filename):
    """Get the multilingual datafile instance with this name.
    """
    return DataFile(
        filename,
        DOWNLOAD_URL,
        DATA_DIR.joinpath(filename.rsplit(".", 1)[0]),
        is_archived=True,
    )


# def are_links_split(datafile, languages):
#     """Check if the links datafile has been split by language.
#     """
#     lg_pairs = [(lg1, lg2) for lg1 in languages for lg2 in languages]
#     versions = [vs for vs in [Links(*pair).version for pair in lg_pairs] if vs]

#     return versions and all(vs == datafile.version for vs in versions)


# def are_audios_split(datafile, languages):
#     """Check if the audios datafile has been split by language.
#     """
#     versions = [vs for vs in [Audios(lg).version for lg in languages] if vs]

#     return versions and all(vs == datafile.version for vs in versions)


def get_language_index(*language_codes):
    """Get the index that maps the sentences' ids to their language.
    """
    logging.info("mapping sentences' ids to languages")

    return {str(s.id): s.lang for lg in language_codes for s in Sentences(lg)}
