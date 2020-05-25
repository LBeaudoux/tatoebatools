import logging

from .config import DATA_DIR
from .datafile import DataFile

logger = logging.getLogger(__name__)


class Table:
    """A Tatoeba table.
    """

    def __init__(self, name, languages):
        # the name of this table
        self._name = name
        # the languages in which some data is required
        self._lgs = languages

    def index(self, key_column, value_column):
        """Get the index that maps 2 columns of this table.
        """
        tbl_index = {}
        for df in self.language_detafiles:
            tbl_index.update(df.index(key_column, value_column))

        return tbl_index

    def classify(self, language_index=None):
        """Classify this table data by language.
        """
        if self.name == "sentences_detailed":
            self.main_datafile.split(columns=[1])
        elif self.name == "sentences_CC0":
            self.main_datafile.split(columns=[1])
        elif self.name == "transcriptions":
            self.main_datafile.split(columns=[1])
        elif self.name == "user_languages":
            self.main_datafile.split(columns=[0])
        elif self.name == "queries":
            self.main_datafile.split(columns=[1])
        elif self.name == "links" and language_index:
            self.main_datafile.split(columns=[0, 1], index=language_index)
        elif self.name == "tags" and language_index:
            self.main_datafile.split(columns=[0], index=language_index)
        elif self.name == "sentences_in_lists" and language_index:
            self.main_datafile.split(columns=[1], index=language_index)
        elif self.name == "jpn_indices" and language_index:
            self.main_datafile.split(columns=[0], index=language_index)
        elif self.name == "sentences_with_audio" and language_index:
            self.main_datafile.split(columns=[0], index=language_index)

    @property
    def name(self):
        """Get the name of this table.
        """
        return self._name

    @property
    def path(self):
        """Get the local path of this table.
        """
        return DATA_DIR.joinpath(self._name)

    @property
    def main_datafile(self):
        """Get the multilingual datafile of this table.
        """
        main_filename = f"{self.name}.csv"
        delimiter = "," if self.name == "queries" else "\t"
        fp = self.path.joinpath(main_filename)

        return DataFile(fp, delimiter=delimiter)

    @property
    def language_detafiles(self):
        """Get the monolingual datafiles of this table.
        """
        if self.name in (
            "sentences_detailed",
            "sentences_CC0",
            "transcriptions",
            "tags",
            "sentences_in_lists",
            "jpn_indices",
            "sentences_with_audio",
            "user_languages",
        ):
            filenames = [f"{lg}_{self.name}.tsv" for lg in self._lgs]
            delimiter = "\t"
        elif self.name in ("queries",):
            filenames = [f"{lg}_{self.name}.csv" for lg in self._lgs]
            delimiter = ","
        elif self.name in ("links",):
            filenames = [
                f"{lg1}-{lg2}_{self.name}.tsv"
                for lg1 in self._lgs
                for lg2 in self._lgs
            ]
            delimiter = "\t"
        else:
            return []

        filepaths = [self.path.joinpath(fn) for fn in filenames]

        return [DataFile(fp, delimiter=delimiter) for fp in filepaths]
