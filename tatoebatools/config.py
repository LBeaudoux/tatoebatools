from pathlib import Path

from pkg_resources import resource_filename

DATA_DIR = Path(resource_filename(__package__, "data"))

SUPPORTED_TABLES = (
    "sentences_base",
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
)

DIFFERENCE_TABLES = (
    "sentences_base",
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
)

TABLE_PARAMS = {
    "sentences_base": {"nb_cols": 2},
    "sentences_detailed": {"nb_cols": 6},
    "sentences_CC0": {"nb_cols": 4},
    "transcriptions": {"nb_cols": 5},
    "links": {"nb_cols": 2},
    "tags": {"nb_cols": 2},
    "user_lists": {"text_col": 4, "nb_cols": 6},
    "sentences_in_lists": {"nb_cols": 2},
    "jpn_indices": {"nb_cols": 3},
    "sentences_with_audio": {"nb_cols": 4},
    "user_languages": {"text_col": -1, "nb_cols": 4},
    "queries": {"delimiter": ",", "text_col": -1, "nb_cols": 3},
}
