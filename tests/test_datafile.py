from io import StringIO
from unittest.mock import patch

from tatoebatools.datafile import (
    DataFile,
    _custom_reader,
    _get_mapped_fields,
    _unsplit_field,
)
from tatoebatools.exceptions import NoDataFile


class TestUnsplitField:
    def test_without_split_field(self):
        row = ["foobar", "text not split by delimiters"]
        new_row = _unsplit_field(row, nb_cols=2, delimiter=",", index_field=-1)
        assert new_row == row

    def test_with_end_split_field(self):
        row = ["foobar", "text", " split", " by", " delimiters"]
        ok_row = ["foobar", "text, split, by, delimiters"]
        new_row = _unsplit_field(row, nb_cols=2, delimiter=",", index_field=-1)
        assert new_row == ok_row

    def test_with_midlle_split_field(self):
        row = ["foobar", "text", " split", " by", " delimiters", "foo"]
        ok_row = ["foobar", "text, split, by, delimiters", "foo"]
        new_row = _unsplit_field(row, nb_cols=3, delimiter=",", index_field=1)
        assert new_row == ok_row


class TestCustomReader:
    def test_with_commas(self):
        str_io = StringIO("a,b,c\n")
        rows = [row for row in _custom_reader(str_io, ",", -1)]
        assert rows == [["a", "b", "c"]]

    def test_with_multiple_rows(self):
        str_io = StringIO("a,b,c\nd,e,f\n")
        rows = [row for row in _custom_reader(str_io, ",", -1)]
        assert rows == [["a", "b", "c"], ["d", "e", "f"]]

    def test_with_tabs(self):
        str_io = StringIO("a\tb\tc\n")
        rows = [row for row in _custom_reader(str_io, "\t", -1)]
        assert rows == [["a", "b", "c"]]

    def test_with_null_field(self):
        str_io = StringIO("a,\\N,c\n")
        rows = [row for row in _custom_reader(str_io, ",", -1)]
        assert rows == [["a", "\\N", "c"]]

    def test_with_split_end_column(self):
        str_io = StringIO("a,b,c\nd,e,f,f")
        rows = [row for row in _custom_reader(str_io, ",", -1)]
        assert rows == [["a", "b", "c"], ["d", "e", "f,f"]]

    def test_with_split_middle_column(self):
        str_io = StringIO("a,b,c\nd,e,e,f")
        rows = [row for row in _custom_reader(str_io, ",", 1)]
        assert rows == [["a", "b", "c"], ["d", "e,e", "f"]]

    def test_with_multiline_row(self):
        str_io = StringIO(
            "abk\t4\tbackstreetboys\tunited states\n"
            "\\\n"
            "American flag\n"
            "\\\n"
            "\n"
        )
        rows = [row for row in _custom_reader(str_io, "\t", -1)]
        assert rows == [
            [
                "abk",
                "4",
                "backstreetboys",
                "united states \\ American flag \\ ",
            ]
        ]


class TestGetMappedFields:
    def test_without_index(self):
        row = ["foo", "bar"]
        columns = [1]
        index = {}
        assert _get_mapped_fields(row, columns, index) == ["bar"]

    def test_with_too_short_row(self):
        row = ["foo", "bar"]
        columns = [2]
        index = {}
        assert _get_mapped_fields(row, columns, index) == [""]

    def test_with_index(self):
        row = ["23", "42"]
        index = {"23": "foo", "42": "bar"}
        columns = [0, 1]
        assert _get_mapped_fields(row, columns, index) == ["foo", "bar"]


class TestDataFile:
    fake_string_io = StringIO("42,fra,foo\n123,eng,bar\n")
    fake_table = [
        ["42", "fra", "foo"],
        ["123", "eng", "bar"],
    ]

    @patch("builtins.open")
    @patch("tatoebatools.datafile.Path.is_file")
    def test_iter_with_file(self, m_isfile, m_open):
        m_isfile.return_value = True
        m_open.return_value = self.fake_string_io
        df = DataFile("any_file_path", delimiter=",", text_col=-1)

        assert [row for row in df] == self.fake_table
        assert m_isfile.call_count == 1
        assert m_open.call_count == 1

    @patch("tatoebatools.datafile.DataFile.__iter__")
    def test_index_with_ok_rows(self, m_iter):
        m_iter.return_value = iter(self.fake_table)
        df = DataFile("any_file_path", delimiter=",", text_col=-1)

        assert df.index(0, 1) == {"42": "fra", "123": "eng"}
        assert m_iter.call_count == 1

    @patch("tatoebatools.datafile.DataFile.__iter__")
    def test_index_with_bad_rows(self, m_iter):
        m_iter.return_value = iter([["42", "fra", "foobar"], ["123"]])
        df = DataFile("any_file_path", delimiter=",", text_col=-1)

        assert df.index(0, 1) == {"42": "fra"}
        assert m_iter.call_count == 1

    @patch("tatoebatools.datafile.DataFile.__iter__")
    def test_index_with_no_datafile(self, m_iter):
        m_iter.side_effect = NoDataFile
        df = DataFile("any_file_path", delimiter=",", text_col=-1)

        assert df.index(0, 1) == {}
        assert m_iter.call_count == 1

    @patch("tatoebatools.datafile.Buffer")
    @patch("tatoebatools.datafile.tqdm")
    @patch("tatoebatools.datafile.logger")
    @patch("tatoebatools.datafile.DataFile.__iter__")
    def test_split_without_index(self, m_iter, m_logger, m_tqdm, m_buffer):
        m_iter.return_value = iter(self.fake_table)
        fp = "any_file_path"
        df = DataFile(fp, delimiter=",", text_col=-1)
        df.split(columns=[1])

        add_args = m_buffer.return_value.add.call_args_list
        assert add_args[0][0][0] == self.fake_table[0]
        assert add_args[1][0][0] == self.fake_table[1]
        assert add_args[0][0][1] != add_args[1][0][1]
        assert m_iter.call_count == 1
        assert m_buffer.return_value.clear.call_count == 1
        assert m_logger.info.call_count == 1
        assert m_tqdm.return_value.update.call_count == 2
        assert m_tqdm.return_value.close.call_count == 1

    @patch("tatoebatools.datafile.Buffer")
    @patch("tatoebatools.datafile.tqdm")
    @patch("tatoebatools.datafile.logger")
    @patch("tatoebatools.datafile.DataFile.__iter__")
    def test_split_with_index(self, m_iter, m_logger, m_tqdm, m_buffer):
        m_iter.return_value = iter(self.fake_table)
        fp = "any_file_path"
        df = DataFile(fp, delimiter=",", text_col=-1)
        ind = {"42": "fra", "123": "eng"}
        df.split(columns=[0], index=ind)

        add_args = m_buffer.return_value.add.call_args_list
        assert add_args[0][0][0] == self.fake_table[0]
        assert add_args[1][0][0] == self.fake_table[1]
        assert add_args[0][0][1] != add_args[1][0][1]
        assert m_iter.call_count == 1
        assert m_buffer.return_value.clear.call_count == 1
        assert m_logger.info.call_count == 1
        assert m_tqdm.return_value.update.call_count == 2
        assert m_tqdm.return_value.close.call_count == 1

    def test_get_out_filename_csv(self):
        fp = "any_file_path"
        df = DataFile(fp, delimiter=",", text_col=-1)

        assert df._get_out_filename(["eng", "fra"]) == f"eng-fra_{fp}.csv"

    def test_get_out_filename_tsv(self):
        fp = "any_file_path"
        df = DataFile(fp, delimiter="\t", text_col=-1)

        assert df._get_out_filename(["eng", "fra"]) == f"eng-fra_{fp}.tsv"
