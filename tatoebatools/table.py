import logging
from pathlib import Path

from .config import (
    DATA_DIR,
    TABLE_CLASSES,
    TABLE_CSV_PARAMS,
    TABLE_DATAFRAME_PARAMS,
)
from .datafile import DataFile
from .exceptions import NotLanguage, NotLanguagePair, NotTable
from .update import Update, check_languages, check_tables

logger = logging.getLogger(__name__)


class Table:
    """A Tatoeba data file handler

    It manages the local update, the parsing and the conversion to dataframe
    of monolingual and multilingual data files downloaded from:
    https://downloads.tatoeba.org/exports/
    """

    def __init__(
        self,
        name,
        language_codes=[],
        data_dir=None,
        scope="all",
        row_filters=[],
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
        row_filters : list, optional
            Row filters are passed to load only useful rows into memory.
            A row filter is a dict containing:
            'col_index': the column for which the rows are filtered by value
            'ok_values': the allowed values in the filter column
            'converter' (optional): a converter applied to the filter column
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
        NotTable
            raised when the table name is not valid
        """
        self._name = name
        self._lgs = language_codes
        self._data_dir = Path(data_dir) if data_dir else DATA_DIR
        self._scp = scope
        self._upd = update
        self._vb = verbose
        self._rf = row_filters

        # check validity of arguments
        self._check_table_name_validity()
        self._check_language_codes_validity()

        # unlike other cases, the links from sentences in one language to
        # sentences in every language are not loaded from a bilingual
        # datafile but filtered from the large 'links.csv'file'
        self._flg = self._get_filter_lang()

        # run necessary updates
        if self._upd:
            self._update_required_files()

        self._dfile = self._build_datafile()
        self._it = iter(self._dfile)

    def __iter__(self):

        self._it = iter(self._dfile)

        return self

    def __next__(self):

        row = next(self._it)

        return TABLE_CLASSES[self._name](*row)

    def as_dataframe(self, **parameters):
        """Get the pandas dataframe of this 'Table'
        Only arguments supported by 'pandas.read_csv' are valid

        Returns
        -------
        pandas.DataFrame
            the dataframe version of this 'Table'
        """
        params = self._get_dataframe_params(self._name, self._lgs, self._scp)
        params.update(parameters)

        return self._dfile.as_dataframe(**params)

    @property
    def path(self):
        """Gzt the path of this 'Table' data file

        Returns
        -------
        pathlib.Path
            The local path of the file containing data for this 'Table'
        """

        return self._get_file_path(
            table_name=self._name,
            language_codes=self._lgs,
            scope=self._scp,
        )

    def _check_table_name_validity(self):
        """Checks if the name of this 'Table' is valid"""
        if self._name not in set(check_tables()):
            raise NotTable(self._name)

    def _check_language_codes_validity(self):
        """Checks if the language code(s) of this 'Table' is/are valid"""
        all_languages = set(check_languages()) | {"*"}
        not_available_langs = set(self._lgs) - all_languages
        if self._name == "links":
            if len(self._lgs) != 2 or not_available_langs:
                raise NotLanguagePair(self._lgs)
        elif len(self._lgs) > 1 or not_available_langs:
            raise NotLanguage(self._lgs)

    def _get_filter_lang(self):
        """Identifies the language for which link rows need to be filtered"""
        is_filter = (
            self._name == "links"
            and "*" in self._lgs
            and set(self._lgs) != {"*"}
        )
        if is_filter:
            flg = next(lg for lg in self._lgs if lg != "*")
            idx = 0 if self._lgs[0] == flg else 1
            return {"lang": flg, "index": idx}

        return {"lang": None, "index": None}

    def _update_required_files(self):
        """Triggers the update of required data files"""
        q = [(self._name, self._lgs)]
        if self._flg["lang"]:  # update filtered sentence ids
            q.append(("sentences_detailed", [self._flg["lang"]]))
        update = Update(q, data_dir=self._data_dir)

        update.run(verbose=self._vb)

    def _build_datafile(self):

        dfile = self._get_datafile(self._name, self._lgs, self._scp)
        if self._flg["lang"]:  # 'links' with one '*' case
            sent_dfile = self._get_datafile(
                "sentences_detailed",
                [self._flg["lang"]],
                "all",
            )
            if self._rf:
                new_filter = {
                    "col_index": self._flg["index"],
                    "ok_values": set(sent_dfile.as_dataframe(usecols=[0])[0]),
                    "converter": int,
                }
                self._rf.append(new_filter)
                return dfile.extract_rows(row_filters=self._rf)
            else:  # faster
                ids_dframe = sent_dfile.as_dataframe(usecols=[0])
                return dfile.join(
                    ids_dframe, index_col=[0], on_col=[self._flg["index"]]
                )

        return dfile.extract_rows(row_filters=self._rf)

    def _get_datafile(self, table_name, language_codes, scope):

        fp = self._get_file_path(table_name, language_codes, scope)
        params = self._get_file_csv_params(table_name, language_codes, scope)
        dfile = DataFile(fp, **params)

        if not dfile.exists():
            self._log_no_data(table_name, language_codes, scope)

        return dfile

    def _log_no_data(self, table_name, language_codes, scope):
        """Logs a warning message when no data file is found"""
        loc_string = "locally " if not self._upd else ""
        msg = (
            f"no data {loc_string}available for table '{table_name}' "
            f"in {language_codes} with scope '{scope}'"
        )
        logger.warning(msg)

    def _get_dataframe_params(self, table_name, language_codes, scope):
        """Gets the 'pandas.read_csv' parameters for this table name,
        language(s) and scope
        """
        return TABLE_DATAFRAME_PARAMS[table_name].copy()

    def _get_file_csv_params(self, table_name, language_codes, scope):
        """Gets the DataFile constructor parameters for this table name,
        language(s) and scope
        """
        return TABLE_CSV_PARAMS[table_name].copy()

    def _get_file_path(self, table_name, language_codes, scope):
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
