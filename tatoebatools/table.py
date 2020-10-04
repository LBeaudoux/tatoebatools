import logging

from .config import DATA_DIR
from .datafile import DataFile
from .version import version

logger = logging.getLogger(__name__)


class Table:
    """A Tatoeba table."""

    def __init__(self, name, languages):
        # the name of this table
        self._name = name
        # the languages in which some data is required
        self._lgs = languages

    def index(self, key_column, value_column):
        """Get the index that maps 2 columns of this table."""
        tbl_index = {}
        for df in self.language_detafiles:
            tbl_index.update(df.index(key_column, value_column))

        return tbl_index

    def classify(self, language_index=None):
        """Classify this table data by language."""
        if self.name == "user_languages":
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
        else:
            return []

        for fs in self.language_filestems:
            version[fs] = self.main_datafile.version

        return self.language_detafiles

    @property
    def name(self):
        """Get the name of this table."""
        return self._name

    @property
    def path(self):
        """Get the local path of this table."""
        return DATA_DIR.joinpath(self._name)

    @property
    def main_datafile(self):
        """Get the multilingual datafile of this table."""
        main_filename = f"{self.name}.csv"
        delimiter = "," if self.name == "queries" else "\t"
        fp = self.path.joinpath(main_filename)

        return DataFile(fp, delimiter=delimiter)

    @property
    def language_detafiles(self):
        """Get the monolingual datafiles of this table."""
        language_datafiles = []
        for fn in self.language_filenames:
            fp = self.path.joinpath(fn)
            delimiter = "\t" if fp.suffix == ".tsv" else ","
            language_datafiles.append(DataFile(fp, delimiter=delimiter))

        return language_datafiles

    @property
    def language_filenames(self):
        """Get the names of the monolingual datafiles"""
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
            return [f"{lg}_{self.name}.tsv" for lg in self._lgs]
        elif self.name in ("queries",):
            return [f"{lg}_{self.name}.csv" for lg in self._lgs]
        elif self.name in ("links",):
            return [
                f"{lg1}-{lg2}_{self.name}.tsv"
                for lg1 in self._lgs
                for lg2 in self._lgs
            ]
        else:
            return []

    @property
    def language_filestems(self):
        """Get the stems of the monolingual datafiles"""
        return [fn.rsplit(".")[0] for fn in self.language_filenames]
