from .config import DATA_DIR
from .datafile import DataFile
from .download import Download
from .index import Index

DOWNLOAD_URL = "https://downloads.tatoeba.org"


class Table:
    """A Tatoeba table.
    """

    def __init__(self, name, languages):
        # the name of this table
        self._name = name
        # the languages in which some data is required
        self._lgs = languages

    def update(self):
        """Update this table for these languages on this machine.
        """
        for dl in self.downloads:
            is_fetched = dl.fetch()
            if is_fetched and self.name in (
                "sentence",
                "sentences_detailed",
                "sentences_CC0",
            ):
                for df in self.language_detafiles:
                    Index(df, 0, 1)

        return is_fetched

    def classify(self, language_index):
        """Classify this table data by language.
        """
        if self.name == "links" and language_index:
            self.main_datafile.split(columns=[0, 1], index=language_index)
        elif self.name == "tags" and language_index:
            self.main_datafile.split(columns=[0], index=language_index)
        elif self.name == "sentences_in_lists" and language_index:
            self.main_datafile.split(columns=[1], index=language_index)
        elif self.name == "jpn_indices" and self.language_index:
            self.main_datafile.split(columns=[0], index=language_index)
        elif self.name == "sentences_with_audio" and language_index:
            self.main_datafile.split(columns=[0], index=language_index)
        elif self.name == "user_languages":
            self.main_datafile.split(columns=[0])
        elif self.name == "queries":
            self.main_datafile.split(columns=[1])

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
        if (
            self.name
            in (
                "sentence",
                "sentences_detailed",
                "sentences_CC0",
                "transcriptions",
            )
            and self._lgs
        ):
            filenames = [f"{lg}_{self.name}.tsv" for lg in self._lgs]
        elif self.name in (
            "sentence",
            "sentences_detailed",
            "sentences_CC0",
            "transcriptions",
            "tags",
            "sentences_in_lists",
            "jpn_indices",
            "sentences_with_audio",
            "user_languages",
            "queries",
        ):
            filenames = [f"{lg}_{self.name}.csv" for lg in self._lgs]
        elif self.name in ("links",):
            filenames = [
                f"{lg1}-{lg2}_{self.name}.csv"
                for lg1 in self._lgs
                for lg2 in self._lgs
            ]
        else:
            return []

        delimiter = "," if self.name == "queries" else "\t"
        filepaths = [self.path.joinpath(fn) for fn in filenames]

        return [DataFile(fp, delimiter=delimiter) for fp in filepaths]

    @property
    def downloads(self):
        """List the downloads used to update the local Tatoeba data.
        """
        downloads = []
        if (
            self.name
            in {
                "sentence",
                "sentences_detailed",
                "sentences_CC0",
                "transcriptions",
            }
            and self._lgs
        ):
            downloads.extend(
                [
                    Download(
                        f"{lg}_{self.name}.tsv",
                        f"{DOWNLOAD_URL}/exports/per_language/{lg}",
                        self.path,
                    )
                    for lg in self._lgs
                ]
            )
        elif self.name in {
            "sentence",
            "sentences_detailed",
            "sentences_CC0",
            "transcriptions",
            "links",
            "tags",
            "user_lists",
            "sentences_in_lists",
            "jpn_indices",
            "sentences_with_audio",
            "user_languages",
        }:
            downloads.append(
                Download(
                    f"{self.name}.csv",
                    f"{DOWNLOAD_URL}/exports",
                    self.path,
                    is_archived=True,
                )
            )
        elif self.name in {
            "queries",
        }:
            downloads.append(
                Download(
                    f"{self.name}.csv",
                    f"{DOWNLOAD_URL}/stats",
                    self.path,
                    is_archived=False,
                )
            )

        return downloads