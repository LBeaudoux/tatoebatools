import csv
import logging
from pathlib import Path

from tqdm import tqdm

from .buffer import Buffer
from .difference import compare_csv
from .exceptions import NoDataFile
from .utils import get_byte_size_of_row, lazy_property, get_extended_name
from .version import version

logger = logging.getLogger(__name__)


class DataFile:
    """A file containing table data."""

    def __init__(
        self, file_path, delimiter="\t", quoting=csv.QUOTE_NONE, text_col=-1
    ):
        # the local path of this data file
        self._fp = Path(file_path)
        # the delimiter that distinguishes table columns
        self._dm = delimiter
        # wether the fields are quoted or not
        self._qt = quoting
        # the column that must not be split by delimiters
        self._tc = text_col

    def __iter__(self):

        try:
            with open(self.path, encoding="utf-8") as f:
                for row in _custom_reader(f, self._dm, self._tc):
                    yield row
        except FileNotFoundError:
            logger.debug(f"{self.path} datafile not found")
            raise NoDataFile
        except RuntimeError:  # empty file
            pass

    def find_changes(self, index_col_keys=None):
        """Compare this file with its older version if there is one"""
        logger.info(f"finding changes in {self.name}")

        path_old = self._get_side_path("old")
        diffs = compare_csv(
            path_old,
            self._fp,
            delimiter=self._dm,
            index_col_keys=index_col_keys,
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

    def split(self, columns=[], index=None):
        """Split the file according to the values mapped by the index
        in a chosen set of columns.
        """
        logger.info(f"splitting {self.name}")

        # init the progress bar
        pbar = tqdm(total=self.size, unit="iB", unit_scale=True)
        # init buffer
        buffer = Buffer(self.path.parent, delimiter=self.delimiter)
        # classify the rows
        for row in self:
            mapped_fields = _get_mapped_fields(row, columns, index)

            if all(mapped_fields):
                fname = self._get_out_filename(mapped_fields)
                buffer.add(row, fname)

            # imcrement progress bar by the byte size of the row
            pbar.update(get_byte_size_of_row(row, self.delimiter))

        buffer.clear()

        pbar.close()

    def _get_out_filename(self, mapped_fields):
        """Get the name of the file that corespond to this mapped fields."""
        mapped_fields_string = "-".join(mapped_fields)
        ext = "tsv" if self._dm == "\t" else "csv"

        return f"{mapped_fields_string}_{self.stem}.{ext}"

    def _get_side_path(self, side_tag):
        """Get the path of a side datafile"""
        extended_name = get_extended_name(self._fp, side_tag)

        return self._fp.parent.joinpath(extended_name)

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

    @lazy_property
    def version(self):
        """Get the version datetime of this datafile"""
        return version[self.stem]


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
