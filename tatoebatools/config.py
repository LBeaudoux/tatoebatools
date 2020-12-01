import csv
from pathlib import Path

from pkg_resources import resource_filename

from .jpn_indices import JpnIndex
from .links import Link
from .queries import Query
from .sentences_base import SentenceBase
from .sentences_cc0 import SentenceCC0
from .sentences_detailed import SentenceDetailed
from .sentences_in_lists import SentenceInList
from .sentences_with_audio import SentenceWithAudio
from .tags import Tag
from .transcriptions import Transcription
from .user_languages import UserLanguage
from .user_lists import UserList
from .utils import list_attributes

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

TABLE_CLASSES = {
    "sentences_base": SentenceBase,
    "sentences_detailed": SentenceDetailed,
    "sentences_CC0": SentenceCC0,
    "transcriptions": Transcription,
    "links": Link,
    "tags": Tag,
    "user_lists": UserList,
    "sentences_in_lists": SentenceInList,
    "jpn_indices": JpnIndex,
    "sentences_with_audio": SentenceWithAudio,
    "user_languages": UserLanguage,
    "queries": Query,
}

TABLE_CSV_PARAMS = {
    "sentences_base": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(SentenceBase)),
    },
    "sentences_detailed": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(SentenceDetailed)),
    },
    "sentences_CC0": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(SentenceCC0)),
    },
    "transcriptions": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(Transcription)),
    },
    "links": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(Link)),
    },
    "tags": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(Tag)),
    },
    "user_lists": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "text_col": 4,
        "nb_cols": len(list_attributes(UserList)),
    },
    "sentences_in_lists": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(SentenceInList)),
    },
    "jpn_indices": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(JpnIndex)),
    },
    "sentences_with_audio": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "nb_cols": len(list_attributes(SentenceWithAudio)),
    },
    "user_languages": {
        "delimiter": "\t",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "text_col": 3,
        "nb_cols": len(list_attributes(UserLanguage)),
    },
    "queries": {
        "delimiter": ",",
        "quoting": csv.QUOTE_NONE,
        "quotechar": "",
        "lineterminator": "\n",
        "text_col": 2,
        "nb_cols": len(list_attributes(Query)),
    },
}

TABLE_DATAFRAME_PARAMS = {
    "sentences_base": {
        "names": list_attributes(SentenceBase),
        "index_col": "sentence_id",
        "na_values": ["\\N"],
    },
    "sentences_detailed": {
        "names": list_attributes(SentenceDetailed),
        "index_col": "sentence_id",
        "parse_dates": ["date_added", "date_last_modified"],
        "na_values": ["\\N", "0000-00-00 00:00:00"],
    },
    "sentences_CC0": {
        "names": list_attributes(SentenceCC0),
        "index_col": "sentence_id",
        "parse_dates": ["date_last_modified"],
        "na_values": ["\\N", "0000-00-00 00:00:00"],
    },
    "transcriptions": {
        "names": list_attributes(Transcription),
    },
    "links": {
        "names": list_attributes(Link),
    },
    "tags": {
        "names": list_attributes(Tag),
    },
    "user_lists": {
        "names": list_attributes(UserList),
        "index_col": "list_id",
        "parse_dates": ["date_created", "date_last_modified"],
        "na_values": ["\\N", "0000-00-00 00:00:00"],
    },
    "sentences_in_lists": {
        "names": list_attributes(SentenceInList),
    },
    "jpn_indices": {
        "names": list_attributes(JpnIndex),
    },
    "sentences_with_audio": {
        "names": list_attributes(SentenceWithAudio),
        "na_values": ["\\N"],
    },
    "user_languages": {
        "names": list_attributes(UserLanguage),
        "na_values": ["\\N"],
    },
    "queries": {
        "names": list_attributes(Query),
        "na_values": ["\\N"],
    },
}
