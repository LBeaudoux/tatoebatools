from pathlib import Path
from unittest.mock import patch

from tatoebatools.buffer import Buffer


class TestBuffer:

    dir = "any_dir_path"
    delimiter = ","

    @patch("builtins.open")
    def test_buffer_add_below_max_size(self, m_open):
        buffer = Buffer(self.dir, delimiter=self.delimiter, max_size=10000)
        row = ["foo", "bar", "foobar"]
        fname = "any_filename"
        buffer.add(row, fname)

        assert buffer[fname] == [row]
        assert m_open.call_count == 0

    @patch("tatoebatools.buffer.csv.writer")
    @patch("builtins.open")
    def test_buffer_add_above_max_size(self, m_open, m_writer):
        buffer = Buffer(self.dir, delimiter=self.delimiter, max_size=0)
        row = ["foo", "bar", "foobar"]
        fname = "any_filename"
        buffer.add(row, fname)

        assert buffer[fname] == []
        out_path = Path(self.dir, f"{fname}.part")
        m_open.assert_called_once_with(out_path, mode="a")
        m_writer.return_value.writerows.assert_called_once_with([row])

    @patch("tatoebatools.buffer.Path.rename")
    @patch("tatoebatools.buffer.csv.writer")
    @patch("builtins.open")
    def test_buffer_clear(self, m_open, m_writer, m_rename):
        buffer = Buffer(self.dir, delimiter=self.delimiter, max_size=1000)
        row = ["foo", "bar", "foobar"]
        fname = "any_filename"
        buffer[fname] = [row]
        buffer.clear()

        out_path_part = Path(self.dir, f"{fname}.part")
        out_path = Path(self.dir, fname)
        m_open.assert_called_once_with(out_path_part, mode="a")
        m_writer.return_value.writerows.assert_called_once_with([row])
        m_rename.assert_called_once_with(out_path)
