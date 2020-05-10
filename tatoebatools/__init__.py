import logging

from .config import DATA_DIR
from .datafile import DataFile
from .sentences import Sentences
from .utils import lazy_property

DOWNLOAD_URL = "https://downloads.tatoeba.org"


class Tatoeba:
    """
    """

    def __init__(self, *language_codes):

        self._lgs = language_codes

    def update(self, *table_names):
        """
        """
        # datafile containing sentences has a priority because it is
        # necessary for splitting files by language
        if any(tbl == "sentences_detailed" for tbl in table_names):
            table_names = sorted(
                table_names,
                key=lambda x: x == "sentences_detailed",
                reverse=True,
            )

        datafiles_queue = []
        for tbl in table_names:
            tbl_datafiles = self._get_datafiles(tbl)
            datafiles_queue.extend(tbl_datafiles)

        updated_datafiles = [df.name for df in datafiles_queue if df.fetch()]

        logging.info("classifying data by language")
        for df in datafiles_queue:
            self._classify(df)

        if updated_datafiles:
            logging.info("{} updated".format(", ".join(updated_datafiles)))
        else:
            logging.info("already up to date")

    def _get_datafiles(self, table_name):
        """
        """
        datafiles = []
        if table_name in {
            "sentence",
            "sentences_detailed",
            "sentences_CC0",
            "transcriptions",
        }:
            datafiles.extend(
                [
                    get_monolingual_datafile(f"{table_name}.tsv", lg)
                    for lg in self._lgs
                ]
            )
        elif table_name in {
            "links",
            "tags",
            "user_lists",
            "sentences_in_lists",
            "jpn_indices",
            "sentences_with_audio",
            "user_languages",
        }:
            datafiles.append(get_exports_datafile(f"{table_name}.csv"))
        elif table_name in {
            "queries",
        }:
            datafiles.append(get_stats_datafile(f"{table_name}.csv"))

        return datafiles

    def _classify(self, datafile):
        """"Split multilingual files by language for efficient access
        """
        if datafile.name == "links.csv" and self.language_index:
            datafile.split(columns=[0, 1], index=self.language_index)
        elif datafile.name == "tags.csv" and self.language_index:
            datafile.split(columns=[0], index=self.language_index)
        elif datafile.name == "sentences_in_lists.csv" and self.language_index:
            datafile.split(columns=[1], index=self.language_index)
        elif datafile.name == "jpn_indices.csv" and self.language_index:
            datafile.split(columns=[0], index=self.language_index)
        elif (
            datafile.name == "sentences_with_audio.csv" and self.language_index
        ):
            datafile.split(columns=[0], index=self.language_index)
        elif datafile.name == "user_languages.csv":
            datafile.split(columns=[0])
        elif datafile.name == "queries.csv":
            datafile.split(columns=[1])

    @lazy_property
    def language_index(self):
        """Get the index that maps the sentences' ids to their language.
        """
        return {str(s.id): s.lang for lg in self._lgs for s in Sentences(lg)}

    @property
    def downloadable_tables(self):
        """
        """
        return [
            "sentences_detailed",
            "transcriptions",
            "links",
            "tags",
            "user_lists",
            "sentences_in_lists",
            "jpn_indices",
            "sentences_with_audio",
            "user_languages",
            "queries",
        ]


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
