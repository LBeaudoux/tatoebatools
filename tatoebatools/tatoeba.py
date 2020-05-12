import logging

from .index import Index
from .table import Table
from .utils import lazy_property

logger = logging.getLogger(__name__)


class Tatoeba:
    """A handler for managing Tatoeba data on the client side.
    """

    def __init__(self, *language_codes):
        # the languages for which some Tatoeba data is required
        self._lgs = language_codes

    def update(self, *table_names):
        """Update the tables and classify them by required language.
        """
        # datafile containing sentences comes first because it is
        # necessary for splitting files by language
        sentences_tbl = Table("sentences_detailed", self._lgs)
        if sentences_tbl.update():
            updated_tables = ["sentences_detailed"]
            if not self._lgs:
                sentences_tbl.classify()
        else:
            updated_tables = []

        for tbl_name in table_names:
            if tbl_name == "sentences_detailed":  # already done
                continue

            tbl = Table(tbl_name, self._lgs)
            if tbl.update():
                updated_tables.append(tbl_name)

            if (
                tbl_name in updated_tables
                and not self._lgs
                and tbl_name in ("sentences_CC0", "transcriptions")
            ):
                tbl.classify()

            elif tbl_name in updated_tables and tbl_name in (
                "links",
                "tags",
                "sentences_in_lists",
                "jpn_indices",
                "sentences_with_audio",
            ):
                tbl.classify(self.language_index)

            elif tbl_name in updated_tables and tbl_name in (
                "user_languages",
                "queries",
            ):
                tbl.classify()

            elif "sentences_detailed" in updated_tables and tbl_name in (
                "links",
                "tags",
                "sentences_in_lists",
                "jpn_indices",
                "sentences_with_audio",
            ):
                tbl.classify(self.language_index)

        if updated_tables:
            logger.info("{} updated".format(", ".join(updated_tables)))
        else:
            logger.info("data already up to date")

    @lazy_property
    def language_index(self):
        """Get the index that maps the sentences' ids to their language.
        """
        logger.info("mapping sentence ids to languages")

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
    """Get the mapping between the sentences' ids and their language.
    """
    sentence_tbl = Table("sentences_detailed", languages)
    if languages:
        return {
            id: lg
            for df in sentence_tbl.language_detafiles
            for id, lg in Index(df, 0, 1)
        }
    else:
        return {id: lg for id, lg in Index(sentence_tbl.main_datafile, 0, 1)}
