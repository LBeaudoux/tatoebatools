import csv
import logging
from io import StringIO, TextIOBase
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from .utils import get_byte_size, get_extended_name
from .version import version

logger = logging.getLogger(__name__)


def reset_pos(func):
    """Decorator for reseting previous position in file-like object
    after a method call
    """

    def _reset_pos(self, *args, **kwargs):
        reset_pos = self.pos
        self.pos = 0
        return func(self, *args, **kwargs)
        self.pos = reset_pos

    return _reset_pos


class DataFile:
    """A data file handler"""

    def __init__(
        self,
        file_path_or_data=StringIO(),
        delimiter="\t",
        quoting=csv.QUOTE_NONE,
        quotechar="",
        lineterminator="\n",
        na_values=None,
        text_col=None,
        nb_cols=None,
    ):
        """
        Parameters
        ----------
        file_path_or_data : pathlib.Path, str, StringIO, pd.DataFrame
            The local path of a datafile, or a file-like object, or
            a pandas dataframe, or a data string
        delimiter : str, optional
            the field delimiter used by this data file,
            by default "\t"
        quoting : csv module constant, optional
            the field quoting rule used by this data file,
            by default csv.QUOTE_NONE
        quotechar : str, optional
            A one-character string used to quote fields containing
            special characters, such as the delimiter or quotechar,
            or which contain new-line characters, by default ""
        lineterminator : str, optional
            The string used to terminate lines produced by the csv
            writers, by default "\n"
        na_values : list, optional
            Additional strings to recognize as NA/NaN in dataframes.
            By default the following values are interpreted as NaN:
            ‘’, ‘#N/A’, ‘#N/A N/A’, ‘#NA’, ‘-1.#IND’, ‘-1.#QNAN’,
            ‘-NaN’, ‘-nan’, ‘1.#IND’, ‘1.#QNAN’, ‘<NA>’, ‘N/A’, ‘NA’,
            ‘NULL’, ‘NaN’, ‘n/a’, ‘nan’, ‘null’, by default None
        text_col : int, optional
            A column that contains texts that may include additional
            delimiter or line terminator characters, by default None
        nb_cols : int, optional
            The expected number of columns per row, by default None
        """
        self._dm = delimiter
        self._qt = quoting
        self._qc = quotechar
        self._lt = lineterminator
        self._na = na_values
        self._tc = text_col
        self._nc = nb_cols

        if isinstance(file_path_or_data, Path):
            try:
                self._f = open(file_path_or_data, encoding="utf-8")
            except FileNotFoundError:  # path with not file scenario
                self._f = StringIO()
            self._fp = file_path_or_data
        elif isinstance(file_path_or_data, str):
            try:
                self._f = open(file_path_or_data, encoding="utf-8")
            except FileNotFoundError:  # data string scenario
                self._f = StringIO(file_path_or_data)
                self._fp = None
            else:
                self._fp = Path(file_path_or_data)
        elif isinstance(file_path_or_data, pd.DataFrame):
            self._f = StringIO()
            file_path_or_data.to_csv(
                self._f,
                sep=self._dm,
                quoting=self._qt,
                quotechar=self._qc,
                line_terminator=self._lt,
                na_rep=self._na[0] if self._na else "",
                header=None,
                index=False,
            )
            self._f.seek(0)
            self._fp = None
        elif isinstance(file_path_or_data, TextIOBase):  # file-like scenario
            self._f = file_path_or_data
            self._f.seek(0)
            self._fp = None
        else:
            data_type = type(file_path_or_data)
            raise TypeError(f"{data_type} is not a valid 'file_path_or_data'")

        # init 'raw row' iterator
        self._rd = csv.reader(
            self._f,
            delimiter=self._dm,
            quoting=self._qt,
            quotechar=self._qc,
            lineterminator=self._lt,
        )
        # init 'working row' value buffer
        self._wr = []

    def __del__(self):

        if self._f:
            self._f.close()

    def __iter__(self):

        self.pos = 0

        return self

    def __next__(self):

        next_row = self._wr
        try:
            if not next_row:  # first line
                next_row = next(self._rd)
            row_cnt = 1
            while True:
                self._wr = next(self._rd)
                if (
                    self._nc
                    and len(next_row) - row_cnt + len(self._wr) <= self._nc
                ):  # cat multiline row
                    next_row.extend(self._wr)
                    row_cnt += 1
                else:
                    break
        except StopIteration:
            self._wr = None
            raise StopIteration
        finally:
            if not next_row:  # reset pos at the end
                self.pos = 0
            else:
                if not self._nc:
                    return next_row
                else:
                    nb_extra_cols = len(next_row) - self._nc
                    if nb_extra_cols > 0:  # field merger required
                        try:
                            i = self._tc
                            j = i + nb_extra_cols + 1
                        except TypeError:
                            msg = f"{self._fp.name} needs a text column"
                            logger.debug(msg)
                        else:  # remove all delimiters from text field
                            next_row[i] = " ".join(next_row[i:j])
                            del next_row[i + 1 : j]

                    if len(next_row) == self._nc:
                        return next_row
                    else:
                        msg = f"bad row in {self.path.name}: {next_row}"
                        logger.debug(msg)

    @reset_pos
    def __str__(self):

        return self._f.read()

    @property
    def pos(self):
        """Get the current position in this datafile"""
        return self._f.tell()

    @pos.setter
    def pos(self, new_pos):
        """Set the position in this datafile"""
        self._f.seek(new_pos)

    @reset_pos
    def as_dataframe(self, **parameters):
        """Get the pandas dataframe of this datafile
        Parameters are any argument supported by 'pandas.read_csv'
        """
        params = {
            "sep": self._dm,
            "quoting": self._qt,
            "quotechar": self._qc,
            "lineterminator": self._lt,
            "na_values": self._na,
            "header": None,
            "index_col": None,
            "names": None,
        }
        params.update(**parameters)
        index_col = params.pop("index_col", None)

        if self._tc:  # fix file buffer when risk of multiline rows
            self._f = self._get_fixed_file_buffer()

        try:
            df = pd.read_csv(self._f, **params)
        except pd.errors.EmptyDataError:
            col_names = params.get("usecols", params["names"])
            return pd.DataFrame(columns=col_names)
        else:
            # separate index setting from reading to avoid FutureWarning:
            # elementwise comparison failed; returning scalar instead,
            # but in the future will perform elementwise comparison
            # mask |= (ar1 == a)
            if index_col:
                df.set_index(index_col, inplace=True)

            return df

    def exists(self):
        """Check if this data file exists locally"""
        return self._fp and self._fp.is_file()

    def save(self, to_path=None, version=None):
        """Save this data file to local path and update the file
        storing version datetimes
        """
        if to_path:
            self._fp = to_path
        with open(self._fp, "w", encoding="utf-8") as f:
            f.write(self._f.getvalue())
        if version:
            self.version = version

    def extract_columns(self, usecols):
        """Extract those columns from this data file"""
        dframe = self.as_dataframe(usecols=usecols)
        try:
            text_col = usecols.index(self._tc)
        except ValueError:
            text_col = None

        return DataFile(
            dframe,
            delimiter=self._dm,
            quoting=self._qt,
            quotechar=self._qc,
            lineterminator=self._lt,
            text_col=text_col,
            nb_cols=len(usecols),
        )

    @reset_pos
    def extract_rows(self, row_filters):
        """Extract those rows from this data file
        A row filter is a dict containing:
        'col_index': the column for which the rows are filtered by value
        'ok_values': the allowed values in the filter column
        'converter' (optional): a converter applied to the filter column
        """
        if row_filters:
            fb = StringIO()
            wt = csv.writer(
                fb,
                delimiter=self._dm,
                quoting=self._qt,
                quotechar=self._qc,
                lineterminator=self._lt,
            )
            for row in self:
                try:
                    for flt in row_filters:
                        field = row[flt["col_index"]]
                        if flt.get("converter"):
                            field = flt["converter"](field)
                        assert field in flt["ok_values"]
                except AssertionError:
                    continue
                else:
                    wt.writerow(row)
            fb.seek(0)

            return DataFile(
                fb,
                delimiter=self._dm,
                quoting=self._qt,
                quotechar=self._qc,
                lineterminator=self._lt,
                text_col=self._tc,
                nb_cols=self._nc,
            )

        return self

    def join(self, other_data, index_col, on_col):
        """Join some indexed data on this datafile"""
        dframe = self.as_dataframe()
        if isinstance(other_data, pd.DataFrame):
            other_dframe = other_data.set_index(index_col)
        elif isinstance(other_data, DataFile):
            other_dframe = other_data.as_dataframe(index_col=index_col)
        join_dframe = dframe.join(
            other_dframe,
            on=on_col,
            how="inner",
            lsuffix="left",
            rsuffix="right",
        )

        return DataFile(
            join_dframe,
            delimiter=self._dm,
            quoting=self._qt,
            quotechar=self._qc,
            lineterminator=self._lt,
            text_col=self._tc,
            nb_cols=self._nc,
        )

    def find_changes(self, verbose=True, save=True):
        """Find 'added' and 'removed' rows to this data file
        compared to its former local version (if any)
        """
        fname_old = get_extended_name(self.path, "old")
        dfile_old = DataFile(
            self.path.parent.joinpath(fname_old),
            delimiter=self._dm,
            quoting=self._qt,
            quotechar=self._qc,
            lineterminator=self._lt,
            text_col=self._tc,
            nb_cols=self._nc,
        )
        diffs = {}
        if all(x.exists() for x in (self, dfile_old)):
            if verbose:
                msg = f"finding changes in {self.path.name}"
                logger.info(msg)
            try:
                merger = pd.merge(
                    dfile_old.as_dataframe(),
                    self.as_dataframe(),
                    how="outer",
                    indicator=True,
                )
            except pd.errors.MergeError:
                msg = f"merger of {self._fp.name} with {fname_old} failed"
                logger.warning(msg, exc_info=True)
            else:
                tags = {"added": "right_only", "removed": "left_only"}
                for k, v in tags.items():
                    mask = merger["_merge"] == v
                    diff_df = merger.loc[mask].drop(columns="_merge")
                    diffs[k] = DataFile(
                        diff_df,
                        delimiter=self._dm,
                        quoting=self._qt,
                        quotechar=self._qc,
                        lineterminator=self._lt,
                        text_col=self._tc,
                        nb_cols=self._nc,
                    )
                if save:  # save difference files in the same directory
                    for tag, dfile in diffs.items():
                        fname = get_extended_name(self.path, tag)
                        fpath = self.path.parent.joinpath(fname)
                        dfile.save(to_path=fpath)

        return diffs

    @reset_pos
    def split(self, columns=[], verbose=True, save=True):
        """Split the file according to these columns' values"""
        if verbose:
            logger.info(f"splitting {self._fp.name}")
            pbar = tqdm(total=self.size, unit="iB", unit_scale=True)
        else:
            pbar = None

        buffer = {}
        for row in self:
            try:
                fields = [row[col] for col in columns]
            except IndexError:
                logger.debug(f"missing column(s) {columns} in {row}")
            else:
                if all(fields):
                    # classify the rows
                    fname = self._get_out_filename(fields)
                    fb = buffer.setdefault(fname, StringIO())
                    wt = csv.writer(
                        fb,
                        delimiter=self._dm,
                        quoting=self._qt,
                        quotechar=self._qc,
                        lineterminator=self._lt,
                    )
                    wt.writerow(row)

            if pbar:  # imcrement progress bar by the byte size of the row
                pbar.update(get_byte_size(row, self._dm, self._lt))

        splits = []
        for fname, fb in buffer.items():
            split = DataFile(
                fb,
                delimiter=self._dm,
                quoting=self._qt,
                quotechar=self._qc,
                lineterminator=self._lt,
                text_col=self._tc,
                nb_cols=self._nc,
            )
            if save:  # save split files in the same parent directory
                try:
                    split.save(
                        to_path=self._fp.parent.joinpath(fname),
                        version=self.version,
                    )
                except FileNotFoundError:
                    logger.debug("split saving failed", exc_info=True)
                    continue
            splits.append(split)

        if pbar:
            pbar.close()

        return splits

    def _get_fixed_file_buffer(self):
        """Try to fix multiline rows found into the file objext"""
        fb = StringIO()
        wt = csv.writer(
            fb,
            delimiter=self._dm,
            quoting=self._qt,
            quotechar=self._qc,
            lineterminator=self._lt,
        )
        wt.writerows(iter(self))
        fb.seek(0)

        return fb

    def _get_out_filename(self, fields):
        """Get the name of the file that corespond to this mapped fields"""
        fields_string = "-".join(fields)
        ext = "tsv" if self._dm == "\t" else "csv"

        return f"{fields_string}_{self._fp.stem}.{ext}"

    @property
    def path(self):
        """Get the path of this datafile (if any)"""
        return self._fp

    @property
    def delimiter(self):
        """Get the string that delimitate fields in this datafile"""
        return self._dm

    @property
    def quoting(self):
        """The field quoting rule used by this data file"""
        return self._qt

    @property
    def quotechar(self):
        """The one-character string used to quote fields containing
        special characters
        """
        return self._qc

    @property
    def lineterminator(self):
        """The string used to terminate this datafile lines"""
        return self._lt

    @property
    def text_col(self):
        """A text column that may include additional delimiter or
        line terminator characters
        """
        return self._tc

    @property
    def nb_cols(self):
        """The expected number of fields expected in a row"""
        return self._nc

    @property
    def size(self):
        """Get the byte size of this data file"""
        if self.exists():
            return self._fp.stat().st_size
        else:
            return 0

    @property
    def version(self):
        """Get the version datetime of this datafile"""
        return version[self._fp.stem]

    @version.setter
    def version(self, new_version):
        """Set the version of this datafile"""
        version[self._fp.stem] = new_version
