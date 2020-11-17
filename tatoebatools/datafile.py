import csv
import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from .buffer import Buffer
from .difference import compare_csv
from .exceptions import NoDataFile
from .utils import get_byte_size_of_row, get_extended_name
from .version import version

logger = logging.getLogger(__name__)


class DataFile:
    """A data file"""

    def __init__(
        self, file_path, delimiter="\t", quoting=csv.QUOTE_NONE, text_col=None
    ):
        """
        Parameters
        ----------
        file_path : str
            the local path of the datafile
        delimiter : str, optional
            the field delimiter used by this data file,
            by default "\t"
        quoting : csv module constant, optional
            the field quoting rule used by this data file,
            by default csv.QUOTE_NONE
        text_col : int, optional
            the index of a not quoted text field that may contain
            delimiter strings, by default None

        Raises
        ------
        NoDataFile
            raised when data file not found
        """
        self._fp = Path(file_path)
        self._dm = delimiter
        self._qt = quoting
        self._tc = text_col

        try:
            self._f = open(self._fp, encoding="utf-8")
        except FileNotFoundError:
            self._f = None
            raise NoDataFile(self._fp)

    def __del__(self):

        if self._f:
            self._f.close()

    def __iter__(self):

        self._rd = self._get_reader()
        self._nb_cols = None

        return self

    def __next__(self):

        try:
            row = next(self._rd)
            if self._nb_cols is None:
                self._nb_cols = len(row)

            while len(row) != self._nb_cols:
                row = next(self._rd)

            return row
        except StopIteration:
            self._f.seek(0)  # enables multiple iterations over the file
            raise StopIteration

    def get_column_values(self, column_index):
        """Get all values found in this column of this datafile"""
        try:
            col_df = pd.read_csv(
                self._fp,
                sep=self._dm,
                header=None,
                usecols=[column_index],
                quoting=self._qt,
            )
        except pd.errors.EmptyDataError:
            return set()
        else:
            return set(col_df.values.flat)

    def find_changes(self, index_col_keys=None, verbose=True):
        """Compare this file with its older version if there is one"""
        path_old = self._get_side_path("old")
        diffs = compare_csv(
            path_old,
            self._fp,
            delimiter=self._dm,
            quoting=self._qt,
            index_col_keys=index_col_keys,
            verbose=verbose,
        )
        for tag, df in diffs.items():
            out_path = self._get_side_path(tag)
            df.to_csv(
                path_or_buf=out_path,
                sep=self._dm,
                header=False,
                index=False,
                quoting=self._qt,
            )

    def index(self, key_column, value_column):
        """Maps values from two columns of this datafile."""
        try:
            ind = {
                row[key_column]: row[value_column]
                for row in self
                if len(row) > key_column and len(row) > value_column
            }
        except NoDataFile:
            ind = {}

        return ind

    def split(self, columns=[], index=None, verbose=True):
        """Split the file according to the values mapped by the index
        in a chosen set of columns
        """
        if verbose:
            logger.info(f"splitting {self.name}")
            pbar = tqdm(total=self.size, unit="iB", unit_scale=True)
        else:
            pbar = None

        # init buffer
        buffer = Buffer(self.path.parent, delimiter=self.delimiter)
        # classify the rows
        for row in self:
            mapped_fields = _get_mapped_fields(row, columns, index)

            if all(mapped_fields):
                fname = self._get_out_filename(mapped_fields)
                buffer.add(row, fname)

            # imcrement progress bar by the byte size of the row
            if pbar:
                pbar.update(get_byte_size_of_row(row, self.delimiter))

        buffer.clear()

        if pbar:
            pbar.close()

        # lists split datafiles
        split_paths = [
            self._fp.parent.joinpath(fn) for fn in buffer.out_filenames
        ]
        splits = [
            DataFile(
                fp, delimiter=self._dm, quoting=self._qt, text_col=self._tc
            )
            for fp in split_paths
        ]
        for split in splits:
            split.version = self.version

        return splits

    def _get_out_filename(self, mapped_fields):
        """Get the name of the file that corespond to this mapped fields."""
        mapped_fields_string = "-".join(mapped_fields)
        ext = "tsv" if self._dm == "\t" else "csv"

        return f"{mapped_fields_string}_{self.stem}.{ext}"

    def _get_side_path(self, side_tag):
        """Get the path of a side datafile"""
        extended_name = get_extended_name(self._fp, side_tag)

        return self._fp.parent.joinpath(extended_name)

    def _get_reader(self):
        """Get the right data reader for this datafile"""
        if self._tc:
            rd = _custom_reader(self._f, delimiter=self._dm, text_col=self._tc)
        else:
            rd = csv.reader(self._f, delimiter=self._dm, quoting=self._qt)

        return rd

    @property
    def path(self):
        """Get the path of this datafile"""
        return self._fp

    @property
    def delimiter(self):
        """Get the string that delimitate fields in this datafile"""
        return self._dm

    @property
    def name(self):
        """Get the name of this datafile"""
        return self._fp.name

    @property
    def stem(self):
        """Get the name of this datafile without its extension"""
        return self._fp.stem

    @property
    def size(self):
        """Get the byte size of this data file"""
        if self._fp.is_file():
            return self._fp.stat().st_size
        else:
            return 0

    @property
    def version(self):
        """Get the version datetime of this datafile"""
        return version[self.stem]

    @version.setter
    def version(self, new_version):
        """Set the version of this datafile"""
        version[self.stem] = new_version


def _unsplit_field(row, nb_cols, delimiter, index_field):
    """Regroup the chosen field of a csv row if split by mistake. Useful if
    the fields are not quoted or if extra delimiters are not escaped.
    """
    if index_field < 0:
        index_field = nb_cols + index_field

    nb_extra = len(row) - nb_cols
    if nb_extra > 0:
        fields_to_join = row[index_field : index_field + nb_extra + 1]
        row[index_field] = delimiter.join(fields_to_join)
        del row[index_field + 1 : index_field + nb_extra + 1]

    return row


def _custom_reader(string_io, delimiter, text_col):
    """A customized version of csv.reader that:
    - unsplit unquoted field that contain delimiters
    - regroup unquoted multiline fields (i.e. containing newline characters)
    """
    reader = csv.reader(
        string_io,
        delimiter=delimiter,
        quoting=csv.QUOTE_NONE,
    )
    # count the number of columns in a regular row
    nb_cols = len(next(reader))
    string_io.seek(0)

    real_row = []
    for row in reader:
        # regroup text field if split by delimiter
        if text_col:
            row = _unsplit_field(row, nb_cols, delimiter, text_col)

        # regroup multiline end fields
        if len(row) == nb_cols:
            if real_row:
                yield real_row
                real_row = []
            real_row.extend(row)
        elif len(row) == 1 and real_row:
            real_row[-1] += " " + row[0]
        elif not row and real_row:
            real_row[-1] += " "
        else:
            logger.debug(f"row skipped: {row}")
    if real_row:
        yield real_row


def _get_mapped_fields(row, columns, index):
    """For this row, get the values of the fields in these columns.
    If index is True, get the value mapped by the index dictionary.
    """
    mapped_fields = []
    for col in columns:
        if len(row) > col:
            val = row[col]

            if index:
                val = index.get(val)

            mapped_fields.append(val)
        else:
            mapped_fields.append("")
            logger.debug(f"{row} does not have column {col}")

    return mapped_fields
