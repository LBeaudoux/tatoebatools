import csv
import logging
from io import StringIO
from pathlib import Path

import pandas as pd

from .config import (
    DATA_DIR,
    TABLE_CLASSES,
    TABLE_CSV_PARAMS,
    TABLE_DATAFRAME_PARAMS,
)
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
        NotTable
            raised when the table name is not valid
        """
        self._name = name
        self._lgs = language_codes
        self._data_dir = Path(data_dir) if data_dir else DATA_DIR
        self._scp = scope
        self._upd = update
        self._vb = verbose

        self._f = None  # init file-like object

        # check validity of arguments
        self._check_table_name_validity()
        self._check_language_codes_validity()

        # unlike other cases, the links from sentences in one language to
        # sentences in every language are not loaded from a bilingual
        # datafile but filtered from the large 'links.csv'file'
        self._flt = self._get_filter_lang()

        # run necessary updates
        if self._upd:
            self._update_required_files()

        self._f = self._open()

    def __del__(self):

        self._f.close()

    def __iter__(self):

        csv_params = TABLE_CSV_PARAMS[self._name]
        self._it = csv.reader(self._f, **csv_params)

        return self

    def __next__(self):

        try:
            row = next(self._it)
        except StopIteration:
            self._f.seek(0)  # enables multiple iterations over the file
            raise StopIteration
        else:
            return TABLE_CLASSES[self._name](*row)

    def as_dataframe(self, parse_dates=True):
        """Get the pandas dataframe of this 'Table'

        Parameters
        ----------
        parse_dates : bool, optional
            whether CSV columns containing datetime strings are parsed as
            datetime columns instead of string columns, by default True
            The CSV reading is faster when 'parse_dates' is False.

        Returns
        -------
        pandas.DataFrame
            the dataframe version of this 'Table'
        """
        # the link rows containing the following sentence ids are filtered
        if self._flt["lang"]:
            filter_ids = self._get_filter_ids()
        else:
            filter_ids = None
        # set up the parameters of the pandas CSV reader
        params = TABLE_DATAFRAME_PARAMS[self._name].copy()
        if not parse_dates:
            params.pop("parse_dates", None)

        if filter_ids is not None and filter_ids.index.empty:  # no link file
            col_names = params.get("usecols", params["names"])
            return pd.DataFrame(columns=col_names)
        else:
            df = self._read_csv_as_dataframe(self.path, **params)
        # join main dataframe with index of filter ids
        if not df.empty and filter_ids is not None:
            return df.join(filter_ids, on=self._flt["col_name"], how="inner")

        return df

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
            col_names = TABLE_DATAFRAME_PARAMS[self._name]["names"]
            col_name = col_names[0] if self._lgs[0] == flg else col_names[1]
            return {"lang": flg, "col_name": col_name}

        return {"lang": None, "index": None}

    def _get_filter_ids(self):
        """Gets the ids of the sentences for which link rows are filtered"""
        fp = self._get_file_path(
            "sentences_detailed",
            language_codes=[self._flt["lang"]],
            scope="all",
        )
        params = TABLE_DATAFRAME_PARAMS["sentences_detailed"].copy()
        params.pop("parse_dates", None)  # for faster csv reading
        params.update({"usecols": ["sentence_id"]})  # one col load is faster

        return self._read_csv_as_dataframe(fp, **params)

    def _update_required_files(self):
        """Triggers the update of required data files"""
        q = [(self._name, self._lgs)]
        if self._flt["lang"]:  # update filtered sentence ids
            q.append(("sentences_detailed", [self._flt["lang"]]))
        update = Update(q, data_dir=self._data_dir)

        update.run(verbose=self._vb)

    def _open(self):
        """Gets the file-like object of this 'Table'"""
        if not self._flt["lang"]:  # basic scenario with one file
            f = self._get_file(self.path)
        else:
            # build a file-like object from this 'Table' dataframe
            df_params = TABLE_DATAFRAME_PARAMS[self._name].copy()
            params = {
                k: v for k, v in df_params.items() if k in ("sep", "quoting")
            }
            params.update({"header": None, "index": False, "na_rep": "\\N"})
            df = self.as_dataframe(parse_dates=False)
            csv_string = df.to_csv(**params)

            f = StringIO()
            f.write(csv_string)
            f.seek(0)

        return f

    def _read_csv_as_dataframe(self, file_path, **parameters):
        """Gets the dataframe of a data file"""
        index_col = parameters.pop("index_col", None)
        try:
            df = pd.read_csv(file_path, **parameters)
        except FileNotFoundError:
            if self._f is None:  # avoid duplicate logs
                self._log_no_data()
            col_names = parameters.get("usecols", parameters["names"])
            df = pd.DataFrame(columns=col_names)
        # separate index setting from reading to avoid FutureWarning:
        # elementwise comparison failed; returning scalar instead,
        # but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        if index_col:
            df.set_index(index_col, inplace=True)

        return df

    def _get_file(self, file_path):
        """Get the file object of the main data file of thos 'Table'"""
        try:
            f = open(file_path)
        except FileNotFoundError:
            self._log_no_data()
            return StringIO()
        else:
            return f

    def _log_no_data(self):
        """Logs a warning message when no data file is found"""
        loc_string = "locally " if not self._upd else ""
        msg = (
            f"no data {loc_string}available for table '{self._name}' "
            f"in {self._lgs} with scope '{self._scp}'"
        )
        logger.warning(msg)

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
