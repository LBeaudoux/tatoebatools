import logging
from pathlib import Path

from .config import DATA_DIR, DIFFERENCE_TABLES
from .datafile import DataFile
from .download import Download
from .exceptions import (
    NoDataFile,
    NotAvailableTable,
    NotLanguagePair,
    NotLanguage,
)
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
from .update import check_languages, check_tables, check_updates
from .user_languages import UserLanguage
from .user_lists import UserList

logger = logging.getLogger(__name__)


class Table:
    """A Tatoeba table"""

    _classes = {
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

    _params = {
        "queries": {"delimiter": ",", "text_col": -1},
        "user_lists": {"text_col": 4},
        "user_languages": {"text_col": -1},
    }

    def __init__(
        self,
        name,
        language_codes=[],
        data_dir=None,
        scope="all",
        update=True,
        verbose=True,
    ):
        """
        Parameters
        ----------
        name : str
            the name of this table
        language_codes : list, optional
            the language(s) of the table data, by default []
        data_dir : str, optional
            the directory where the Tatoeba data is saved, by default None
        scope : str, optional
            the scope of the table data (i.e. "all", "removed" or "added"),
            by default "all"
        update : bool, optional
            whether the table data is updated or not, by default True
        verbose : bool, optional
            verbosity level for the various methods, by default True

        Raises
        ------
        NotLanguagePair
            raised when not valid pair of languages codes is passed
        NotLanguage
            raised when not valid language code is passed
        NotAvailableTable
            raised when the table name is not valid
        """
        self._name = name
        self._lgs = language_codes
        self._data_dir = Path(data_dir) if data_dir else DATA_DIR
        self._scp = scope
        self._upd = update
        self._vb = verbose

        # check availability of the table name
        if self._name not in set(check_tables()):
            raise NotAvailableTable([self._name])

        # check validity of language codes
        all_languages = set(check_languages()) | {"*"}
        not_available_langs = set(self._lgs) - all_languages
        if self._name == "links":
            if len(self._lgs) != 2 or not_available_langs:
                raise NotLanguagePair(self._lgs)
        elif len(self._lgs) > 1 or not_available_langs:
            raise NotLanguage(self._lgs)

        # special case with datafile row filtering
        filter_mode = (
            self._name == "links"
            and "*" in self._lgs
            and set(self._lgs) != {"*"}
        )
        if filter_mode:
            self._flg = next(lg for lg in self._lgs if lg != "*")
        else:
            self._flg = None

        if self._upd:
            self._update(table_name=self._name, language_codes=self._lgs)

            if self._flg:
                self._update(
                    table_name="sentences_detailed", language_codes=[self._flg]
                )

        self._f = self._get_datafile(
            table_name=self._name, language_codes=self._lgs, scope=self._scp
        )

    def __iter__(self):

        self._it = iter(self._f)

        if self._flg:
            filter_lang_sentences = self._get_datafile(
                table_name="sentences_detailed",
                language_codes=[self._flg],
                scope="all",
            )
            self._fids = filter_lang_sentences.get_column_values(0)
            self._ind_flg = 0 if self._lgs[0] == self._flg else 1
        else:
            self._fids = None
            self._ind_flg = None

        return self

    def __next__(self):

        row = next(self._it)
        if self._ind_flg is not None:
            while int(row[self._ind_flg]) not in self._fids:
                row = next(self._it)

        return Table._classes[self._name](*row)

    def _update(self, table_name, language_codes):
        """Updates the data file of this table for this language(s)"""
        # get the urls of the datafiles that need an update
        to_download = check_updates(
            [table_name],
            ["*"]
            if (not language_codes or "*" in language_codes)
            else language_codes,
            oriented_pair=True,
            verbose=False,
        )
        if len(to_download) == 1:
            url, vs = next(iter(to_download.items()))

            # download the file of the update
            dl = Download(url, vs, data_dir=self._data_dir)
            dl_paths = dl.fetch(verbose=self._vb)

            if len(dl_paths) == 1:
                tbl_params = Table._params.get(table_name, {})
                dl_datafile = DataFile(dl_paths[0], **tbl_params)
                new_datafiles = {dl_datafile}
                if dl_datafile.stem == "queries":
                    splits = dl_datafile.split(columns=[1], verbose=self._vb)
                    new_datafiles |= set(splits)

                # compare new datafiles with their older version
                for df in new_datafiles:
                    if any(tbl in df.stem for tbl in DIFFERENCE_TABLES):
                        df.find_changes(index_col_keys=None, verbose=self._vb)

    def _get_datafile(self, table_name, language_codes, scope):
        """Get the datafile instance of this table for this language(s)
        and scope
        """
        fp = self._get_datafile_path(
            table_name=table_name,
            language_codes=language_codes,
            scope=scope,
        )

        try:
            params = Table._params.get(table_name, {})
            datafile = DataFile(fp, **params)
        except NoDataFile:
            lg_string = "-".join(language_codes)
            msg = (
                f"no '{scope}' data locally available for the "
                f"'{table_name}' table in {lg_string}."
            )
            logger.warning(msg)
            return
        else:
            return datafile

    def _get_datafile_path(self, table_name, language_codes, scope):
        """Get the path of the datafile of this table for this language(s)
        and scope
        """
        parts = []
        if language_codes and "*" not in language_codes:
            parts.append("-".join(language_codes))
        parts.append(table_name)
        if scope and scope != "all":
            parts.append(scope)
        suffix = (
            "csv"
            if (
                not language_codes
                or "*" in language_codes
                or table_name == "queries"
            )
            else "tsv"
        )

        fname = ".".join(("_".join(parts), suffix))

        return self._data_dir.joinpath("/".join((table_name, fname)))
