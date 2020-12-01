import logging

from .sentences_detailed import SentenceDetailed
from .tatoebatools import Tatoeba

logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)

tatoeba = Tatoeba()


class ParallelCorpus:
    """A parallel corpus of sentences' pairs

    A parallel corpus between two languages is a collection of the
    Tatoeba sentences in the source language placed alongside their
    translations in the target language
    """

    def __init__(
        self,
        source_language_code,
        target_language_code,
        update=True,
        verbose=True,
    ):
        """
        Parameters
        ----------
        source_language_code : str
            The ISO 639-3 code of the parallel corpus' source language
        target_language_code : str
            The ISO 639-3 code of the parallel corpus' target language
        update : bool, optional
            Whether a data file is updated before being read, by default True
        verbose : bool, optional
            Whether update steps are printed, by default True
        """
        self._src_lg = source_language_code
        self._tgt_lg = target_language_code
        self._upd = update
        self._vb = verbose

        self._df = self._get_join_dataframe()
        self._rd = self._df.itertuples(index=False)

    def __iter__(self):

        self._rd = self._df.itertuples(index=False)

        return self

    def __next__(self):

        row = next(self._rd)
        sentence = SentenceDetailed(
            row.sentence_id,
            row.lang_sentence,
            row.text_sentence,
            row.username_sentence,
            row.date_added_sentence,
            row.date_last_modified_sentence,
        )
        translation = SentenceDetailed(
            row.translation_id,
            row.lang_translation,
            row.text_translation,
            row.username_translation,
            row.date_added_translation,
            row.date_last_modified_translation,
        )

        return (sentence, translation)

    def _get_join_dataframe(self):
        """Join source sentence, target sentence, and link dataframes"""
        lk_dframe = self._get_link_dataframe()
        src_row_filters = [
            {
                "col_index": 0,
                "ok_values": set(lk_dframe["sentence_id"]),
                "converter": int,
            }
        ]
        tgt_row_filters = [
            {
                "col_index": 0,
                "ok_values": set(lk_dframe["translation_id"]),
                "converter": int,
            }
        ]
        src_dframe, tgt_dframe = self._get_sentence_dataframes(
            src_row_filters, tgt_row_filters
        )

        return lk_dframe.join(src_dframe, on="sentence_id", how="inner").join(
            tgt_dframe,
            on="translation_id",
            how="inner",
            lsuffix="_sentence",
            rsuffix="_translation",
        )

    def _get_link_dataframe(self):
        """Get the dataframe of all direct translation links from
        the source to the target language
        """
        params = {
            "language_codes": [self._src_lg, self._tgt_lg],
            "scope": "all",
            "update": self._upd,
            "verbose": self._vb,
        }

        return tatoeba.get("links", **params)

    def _get_sentence_dataframes(self, source_row_filters, target_row_filters):
        """Get the dataframes of the source and target sentence tables"""
        params = {
            "scope": "all",
            "update": self._upd,
            "verbose": self._vb,
            "parse_dates": False,  # accelerates CSV file reading
        }

        if "*" in (self._src_lg, self._tgt_lg):
            params["language_codes"] = ["*"]
            src_ok_vals = source_row_filters[0]["ok_values"]
            tgt_ok_vals = target_row_filters[0]["ok_values"]
            params["row_filters"] = [
                {
                    "col_index": 0,
                    "ok_values": src_ok_vals | tgt_ok_vals,
                    "converter": int,
                }
            ]
            src_dframe = tatoeba.get("sentences_detailed", **params)
            tgt_dframe = src_dframe
        else:
            params["language_codes"] = [self._src_lg]
            params["row_filters"] = source_row_filters
            src_dframe = tatoeba.get("sentences_detailed", **params)
            if self._tgt_lg == self._src_lg:
                tgt_dframe = src_dframe
            else:
                params["language_codes"] = [self._tgt_lg]
                params["row_filters"] = target_row_filters
                tgt_dframe = tatoeba.get("sentences_detailed", **params)

        return src_dframe, tgt_dframe
