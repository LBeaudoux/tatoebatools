import logging

from .index import Index
from .table import Table
from .utils import lazy_property


to_index = ("sentences_detailed.tsv", "sentences.tsv", "sentences_CC0.tsv")


class Tatoeba:
    """A handler for managing Tatoeba data on the client side.
    """

    def __init__(self, *language_codes):
        # the languages for which some Tatoeba data is required
        self._lgs = language_codes

    def update(self, *table_names):
        """Update the tables and classify them by required language.
        """
        # datafile containing sentences has a priority because it is
        # necessary for splitting files by language
        # if any(tbl == "sentences_detailed" for tbl in table_names):
        #     table_names = sorted(
        #         table_names,
        #         key=lambda x: x == "sentences_detailed",
        #         reverse=True,
        #     )
        # else:
        #     table_names.insert(0, "sentences_detailed")

        sentences_tbl = Table("sentences_detailed", self._lgs)
        if sentences_tbl.update():
            updated_tables = ["sentences_detailed"]
        else:
            updated_tables = []

        for tbl_name in table_names:
            if tbl_name == "sentences_detailed":  # already done
                continue

            tbl = Table(tbl_name, self._lgs)
            if tbl.update():
                updated_tables.append(tbl_name)

            if tbl_name in updated_tables and tbl_name in (
                "links",
                "tags",
                "sentences_in_lists",
                "jpn_indices",
                "sentences_with_audio",
                "user_languages",
                "queries",
            ):
                tbl.classify(self.language_index)

            elif "sentences_detailed" in updated_tables and tbl_name in (
                "links",
                "tags",
                "sentences_in_lists",
                "jpn_indices",
                "sentences_with_audio",
            ):  
                tbl.classify(self.language_index)

        if updated_tables:
            logging.info("{} updated".format(", ".join(updated_tables)))
        else:
            logging.info("already up to date")

    @lazy_property
    def language_index(self):
        """Get the index that maps the sentences' ids to their language.
        """
        logging.info("mapping sentence ids to languages")

        return get_language_index(*self._lgs)

    @property
    def downloadable_tables(self):
        """
        """
        return [
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


def get_language_index(*languages):
    """
    """
    sentence_tbl = Table("sentences_detailed", languages)

    return {
        id: lg
        for df in sentence_tbl.language_detafiles
        for id, lg in Index(df, 0, 1)
    }
