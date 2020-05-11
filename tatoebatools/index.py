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
        self._ind = self._build()

    def __iter__(self):

        return iter(self._ind.items())

    def _build(self):
        """Build the index from scratch.
        """
        return {row[self._kcol]: row[self._vcol] for row in self._df}
