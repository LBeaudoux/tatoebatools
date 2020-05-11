import json
import logging


class Index:
    """An index that maps values from two columns of a datafile.
    """

    def __init__(self, datafile, key_column, value_colomn):

        # the datafile to be indexed
        self._df = datafile
        # the column from which values are used as the index keys
        self._kcol = key_column
        # the column from which values are used as the index values
        self._vcol = value_colomn
        # the index data
        self._ind = self._load()
        if not self._ind:
            self._ind = self._build()

    def __iter__(self):

        return self._ind.items()

    def get(self):
        """Get the index dictionary
        """
        return self._ind

    def save(self):
        """Save the index into a JSON file.
        """
        try:
            with open(self.path, "w") as f:
                json.dump(self._ind, f)
        except OSError:
            logging.exception(f"error occurred during saving of {self.path}")

    def _build(self):
        """Build the index from scratch.
        """
        return {row[self._kcol]: row[self._vcol] for row in self._df}

    def _load(self):
        """Load the index from its JSON file.
        """
        try:
            with open(self.path) as f:
                ind = json.load(f)
        except OSError:
            return {}
        else:
            return ind

    @property
    def path(self):
        """Get the path of the JSON file where the index is saved.
        """
        return self._df.path.parent.joinpath(self.name)

    @property
    def name(self):
        """Get the name of the JSON file where the index is saved.
        """
        return f"{self._df.path.stem}_index{self._kcol}{self._vcol}.json"
