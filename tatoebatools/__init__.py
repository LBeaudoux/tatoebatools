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
        self._lgs = {"src": source_language_code, "tgt": target_language_code}
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

    @property
    def dataframe(self):
        """Get the dataframe of this parallel corpus

        Returns
        -------
        pandas.DataFrame
            Current parallel corpus loaded into memory as dataframe
        """
        index_cols = ["sentence_id", "translation_id"]

        return self._df.set_index(index_cols).sort_values(by=index_cols)

    def _get_join_dataframe(self):
        """Join source sentence, target sentence, and link dataframes"""
        links = self._get_link_dataframe()
        row_filters = {
            k: [
                {
                    "col_index": 0,
                    "ok_values": set(
                        links[
                            "sentence_id" if k == "src" else "translation_id"
                        ]
                    ),
                    "converter": int,
                }
            ]
            for k in ("src", "tgt")
        }
        sentences = self._get_sentence_dataframes(row_filters)

        return links.join(
            sentences["src"], on="sentence_id", how="inner"
        ).join(
            sentences["tgt"],
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
            "language_codes": [self._lgs[k] for k in ("src", "tgt")],
            "scope": "all",
            "update": self._upd,
            "verbose": self._vb,
        }

        return tatoeba.get("links", **params)

    def _get_sentence_dataframes(self, row_filters):
        """Get the dataframes of the source and target sentence tables"""
        params = {
            "scope": "all",
            "update": self._upd,
            "verbose": self._vb,
            "parse_dates": False,  # accelerates CSV file reading
        }

        if "*" in self._lgs:
            # optimize memory footprint by loading only one dataframe
            params["language_codes"] = ["*"]
            params["row_filters"] = [
                {
                    "col_index": 0,
                    "ok_values": set().union(
                        rf[0]["ok_values"] for rf in row_filters.values()
                    ),
                    "converter": int,
                }
            ]
            df = tatoeba.get("sentences_detailed", **params)
            df.set_index("sentence_id", inplace=True)
            sentences = {k: df for k in ("src", "tgt")}
        else:
            sentences = {}
            for k, lg in self._lgs.items():
                params["language_codes"] = [lg]
                params["row_filters"] = row_filters[k]
                sentences[k] = tatoeba.get("sentences_detailed", **params)
                sentences[k].set_index("sentence_id", inplace=True)
                # avoid multiple loads of same dataframe
                if self._lgs["src"] == self._lgs["tgt"]:
                    sentences["tgt" if k == "src" else "src"] = sentences[k]
                    break

        return sentences
