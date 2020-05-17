import csv
import logging
from pathlib import Path
from sys import getsizeof

from tqdm import tqdm

from .exceptions import NoDataFile

logger = logging.getLogger(__name__)


class DataFile:
    """A file containing table data.
    """

    def __init__(self, file_path, delimiter="\t", text_col=-1):
        # the local path of this data file
        self._fp = Path(file_path)
        # the delimiter that distinguishes table columns
        self._dm = delimiter
        # the column that must not be split by delimiters
        self._tc = text_col

    def __iter__(self):

        try:
            with open(self.path) as f:
                reader = csv.reader(
                    f, delimiter=self._dm, quoting=csv.QUOTE_NONE,
                )
                # count the number of columns in a regular row
                nb_cols = len(next(reader))
                f.seek(0)

                real_row = []
                for row in reader:
                    # regroup text field if split by delimiter
                    if self._tc:
                        row = unsplit_field(row, nb_cols, self._dm, self._tc)

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
                        logger.debug(f"row skipped in {self.path}: {row}")
                if real_row:
                    yield real_row
        except OSError:
            logger.debug(f"an error occurred while reading {self.path}")

            raise NoDataFile

    def split(self, columns=[], index=None, int_key=False):
        """Split the file according to the values mapped by the index
        in a chosen set of columns. 
        """
        logger.info(f"splitting {self.name}")

        # init the progress bar
        pbar = tqdm(total=self.size, unit="iB", unit_scale=True)
        # init buffer
        buffer = Buffer(self.path.parent, delimiter=self._dm)
        # classify the rows
        for row in self:
            mapped_vals = []
            for col in columns:
                if len(row) > col:
                    val = row[col]

                    if index:
                        if int_key:
                            val = int(val)
                        val = index.get(val)

                    mapped_vals.append(val)
                else:
                    mapped_vals.append("")
                    logger.debug(f"{row} does not have column {col}")

            if all(mapped_vals):
                mapped_vals_string = "-".join(mapped_vals)
                ext = "tsv" if self._dm == "\t" else "csv"
                fname = f"{mapped_vals_string}_{self.stem}.{ext}"
                buffer.add(row, fname)

            # imcrement progress bar by the byte size of the row
            line = self._dm.join(row) + "\n"
            pbar.update(len(line.encode("utf-8")))

        buffer.clear()

        pbar.close()

    @property
    def path(self):
        """Get the path of this datafile.
        """
        return self._fp

    @property
    def name(self):
        """Get the name of this datafile.
        """
        return self._fp.name

    @property
    def stem(self):
        """Get the name of this datafile without its extension.
        """
        return self._fp.stem

    @property
    def size(self):
        """Get the byte size of this data file.
        """
        if self.path.is_file():
            return self.path.stat().st_size
        else:
            return 0


class Buffer:
    """A buffer temporarily stores data and then appends it into out files 
    when full. It is useful to avoid memory overflow when handling very large 
    data files.
    """

    def __init__(self, out_dir, delimiter="\t", max_size=10000):
        # directory path where out files are saved.
        self._dir = Path(out_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._fps = set(self._dir.iterdir())  # files already in the out_dir
        # the feed delimiter used in the out files
        self._dm = delimiter
        # maximum number elements in a buffer
        self._max = max_size
        # the buffer data is classified in a dict. The dict keys are named
        # after the out filenames the data is directed to.
        self._data = {}

    def add(self, elt, out_fname):
        """Adds an element into the buffer linked to 'out_fname'. Once the 
        buffer is full, this element is appended to the file at 
        'out_dir/out_fname'.
        """
        if out_fname not in self._data:
            self._data[out_fname] = []
            # reinitialize the out file
            out_fp = Path(self._dir, out_fname)
            if out_fp in self._fps:
                out_fp.unlink()
                self._fps.remove(out_fp)

        self._data.setdefault(out_fname, []).append(elt)

        if getsizeof(self._data[out_fname]) > self._max:
            self._save(out_fname)

    def _save(self, out_fname, end=False):
        """Appends buffered elements into their out datafile and then clears
        the buffer.
        """
        data = self._data[out_fname]
        out_fp = Path(self._dir, f"{out_fname}.part")
        try:
            with open(out_fp, mode="a") as f:
                wt = csv.writer(f, delimiter=self._dm)
                wt.writerows(data)
        except OSError:
            logger.debug(f"an error occured when opening {out_fp}")
        else:
            self._data[out_fname].clear()

            if end:
                # removes '.part' extension
                out_fp.rename(out_fp.parent.joinpath(out_fp.stem))

    def clear(self):
        """Saves the data remaining in the buffer into the corresponding 
        outfiles.
        """
        for out_fname in self._data.keys():
            self._save(out_fname, end=True)

        self._data.clear()

    @property
    def out_filenames(self):
        """List every out file name.
        """
        return list(self._data.keys())


def unsplit_field(row, nb_cols, delimiter, index_field):
    """Regroup the chosen field of a csv row if split by mistake. Useful if
    the fields are not quoted or if extra delimiters are not escaped.w
    """
    if index_field < 0:
        index_field = nb_cols + index_field

    nb_extra = len(row) - nb_cols
    if nb_extra > 0:
        fields_to_join = row[index_field : index_field + nb_extra + 1]
        row[index_field] = delimiter.join(fields_to_join)
        del row[index_field + 1 : index_field + nb_extra + 1]

    return row
