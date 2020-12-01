import csv
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from tatoebatools.datafile import DataFile


class TestDataFileInit:

    data = "a,b,c\nd,e,f\n"
    params = {"delimiter": ","}

    def test_string_arg(self):
        dfile = DataFile(self.data)
        assert str(dfile) == self.data

    @patch("builtins.open")
    def test_path_arg(self, m_open):
        m_open.return_value = StringIO(self.data)
        fp = Path("any/path")
        dfile = DataFile(fp, **self.params)
        assert str(dfile) == self.data

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_file_not_found(self, m_open):
        fp = Path("any/path")
        dfile = DataFile(fp, **self.params)
        assert str(dfile) == ""

    def test_dataframe_arg(self):
        dframe = pd.DataFrame([["a", "b", "c"], ["d", "e", "f"]])
        dfile = DataFile(dframe, **self.params)
        assert str(dfile) == self.data

    def test_file_lik_object_arg(self):
        dfile = DataFile(StringIO(self.data), **self.params)
        assert str(dfile) == self.data


class TestDataFileIterator:

    delimiters = ("\t", ",")

    def test_empty(self):
        for dm in self.delimiters:
            dfile = DataFile("", delimiter=dm)
            assert [row for row in dfile] == []

    def test_one_row(self):
        in_rows = [["aaa", "bbb", "ccc"]]
        for dm in self.delimiters:
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm)
            out_rows = [row for row in dfile]
            assert out_rows == in_rows

    def test_with_multiple_rows(self):
        in_rows = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        for dm in self.delimiters:
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm)
            out_rows = [row for row in dfile]
            assert out_rows == in_rows

    def test_with_null_field(self):
        in_rows = [["a", "\\N", "c"]]
        for dm in self.delimiters:
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm)
            out_rows = [row for row in dfile]
            assert out_rows == in_rows

    def test_delimiter_split_end_column(self):
        for dm in self.delimiters:
            in_rows = [["a", "b", "c", "c"]]
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm, nb_cols=3, text_col=2)
            out_rows = [row for row in dfile]
            assert out_rows == [["a", "b", "c c"]]

    def test_delimiter_split_middle_column(self):
        for dm in self.delimiters:
            in_rows = [["a", "b", "c"], ["d", "e", "e", "f"]]
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm, nb_cols=3, text_col=1)
            out_rows = [row for row in dfile]
            assert out_rows == [["a", "b", "c"], ["d", "e e", "f"]]

    def test_endline_split_end_column(self):
        for dm in self.delimiters:
            in_rows = [["a", "b", "c"], ["c"], ["d", "e", "f"]]
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm, nb_cols=3, text_col=2)
            out_rows = [row for row in dfile]
            assert out_rows == [["a", "b", "c c"], ["d", "e", "f"]]

    def test_endline_split_middle_column(self):
        for dm in self.delimiters:
            in_rows = [["a", "b", "c"], ["d", "e"], ["e", "f"]]
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm, nb_cols=3, text_col=1)
            out_rows = [row for row in dfile]
            assert out_rows == [["a", "b", "c"], ["d", "e e", "f"]]

    def test_quoted_text(self):
        for dm in self.delimiters:
            in_rows = [["foo", 'foo "bar" baz', "bar"]]
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(
                s, delimiter=dm, quotechar="", quoting=csv.QUOTE_NONE
            )
            out_rows = [row for row in dfile]
            assert out_rows == in_rows


class TestDataFileAsDataFrame:

    delimiters = ("\t", ",")

    def test_empty(self):
        for dm in self.delimiters:
            dfile = DataFile("", delimiter=dm)
            dframe = dfile.as_dataframe()
            assert dframe.equals(pd.DataFrame())

    def test_ok_row(self):
        in_rows = [["aaa", "bbb", "ccc"], ["ddd", "eee", "fff"]]
        for dm in self.delimiters:
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm)
            dframe = dfile.as_dataframe()
            assert dframe.equals(pd.DataFrame(in_rows))

    def test_multiline_row(self):
        in_rows = [["aaa", "bb"], ["b", "ccc"], ["ddd", "eee", "fff"]]
        for dm in self.delimiters:
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm, nb_cols=3, text_col=1)
            dframe = dfile.as_dataframe()
            out_rows = [["aaa", "bb b", "ccc"], ["ddd", "eee", "fff"]]
            assert dframe.equals(pd.DataFrame(out_rows))

    def test_with_index_col(self):
        in_rows = [["aaa", "bbb", "ccc"], ["ddd", "eee", "fff"]]
        for dm in self.delimiters:
            s = "\n".join([dm.join(r) for r in in_rows])
            dfile = DataFile(s, delimiter=dm)
            dframe1 = dfile.as_dataframe(index_col=[0])
            dframe2 = pd.DataFrame(in_rows).set_index([0])
            assert dframe1.equals(dframe2)


class TestDataFileExtract:

    delimiters = ("\t", ",")
    data = "a,b,c\nd,e,f\n"
    params = {"delimiter": ","}

    def test_extract_columns(self):
        dfile = DataFile(self.data, **self.params)
        dfile_cols = dfile.extract_columns(usecols=[0, 1])
        assert str(dfile_cols) == str(DataFile("a,b\nd,e\n", **self.params))

    def test_extract_rows(self):
        dfile = DataFile(self.data, **self.params)
        row_filters = [{"col_index": 0, "ok_values": {"d"}}]
        dfile_rows = dfile.extract_rows(row_filters=row_filters)
        assert str(dfile_rows) == str(DataFile("d,e,f\n", **self.params))


class TestDataFileJoin:

    delimiters = ("\t", ",")
    data = "a,b,c\nd,e,f\n"
    params = {"delimiter": ","}

    def test_join_dataframe(self):
        dfile = DataFile(self.data, **self.params)
        other_dframe = pd.DataFrame([["a", "b"], ["c", "d"], ["e", "f"]])
        join_dfile = dfile.join(other_dframe, index_col=[0], on_col=[0])
        assert str(join_dfile) == "a,b,c,b\n"

    def test_join_datafile(self):
        dfile = DataFile(self.data, **self.params)
        other_dfile = DataFile("a,b\nc,d\ne,f", **self.params)
        join_dfile = dfile.join(other_dfile, index_col=[0], on_col=[0])
        assert str(join_dfile) == "a,b,c,b\n"
