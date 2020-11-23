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
        lk_df = self._get_link_dataframe()
        src_df, tgt_df = self._get_sentence_dataframes()

        return lk_df.join(src_df, on="sentence_id", how="inner").join(
            tgt_df,
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

    def _get_sentence_dataframes(self):
        """Get the dataframes of the source and target sentence tables"""
        params = {
            "scope": "all",
            "parse_dates": False,  # accelerates CSV file reading
            "update": self._upd,
            "verbose": self._vb,
        }

        if "*" in (self._src_lg, self._tgt_lg):
            params["language_codes"] = ["*"]
            src_df = tatoeba.get("sentences_detailed", **params)
            tgt_df = src_df
        else:
            params["language_codes"] = [self._src_lg]
            src_df = tatoeba.get("sentences_detailed", **params)
            if self._tgt_lg == self._src_lg:
                tgt_df = src_df
            else:
                params["language_codes"] = [self._tgt_lg]
                tgt_df = tatoeba.get("sentences_detailed", **params)

        return src_df, tgt_df
