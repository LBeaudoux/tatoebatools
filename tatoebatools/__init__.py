import logging

from .index import Index
from .table import Table
from .utils import lazy_property


to_index = ("sentences_detailed.tsv", "sentences.tsv", "sentences_CC0.tsv")


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
        if any(
            tbl in ("sentences", "sentences_detailed") for tbl in table_names
        ):
            table_names = sorted(
                table_names,
                key=lambda x: x in ("sentences", "sentences_detailed"),
                reverse=True,
            )
        else:
            table_names.insert(0, "sentences")

        updated_tables = []
        for tbl_name in table_names:
            tbl = Table(tbl_name, self._lgs)
            if tbl.update():
                updated_tables.append(tbl_name)

                if tbl.name in (
                    "tags",
                    "sentences_in_lists",
                    "jpn_indices",
                    "sentences_with_audio",
                    "user_languages",
                    "queries",
                ):
                    tbl.classify(self.lang_index)

        if updated_tables:
            logging.info("{} updated".format(", ".join(updated_tables)))
        else:
            logging.info("already up to date")

    @lazy_property
    def language_index(self):
        """Get the index that maps the sentences' ids to their language.
        """
        tbl_names = ("sentences", "sentences_detailed")
        sentence_tbl = Table("sentences", self._lgs)

        return {
            id: lg
            for df in sentence_tbl.language_detafiles
            for id, lg in Index(df, 0, 1)
        }

    @property
    def downloadable_tables(self):
        """
        """
        return [
            "sentences",
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
            "queries",
        ]
