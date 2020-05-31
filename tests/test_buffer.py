from pathlib import Path
from unittest.mock import patch

from tatoebatools.buffer import Buffer


class TestBuffer:

    dir = "/my/dir/path"
    delimiter = ","
    fname = "any_filename"
    out_path = "/my/dir/path/any_filename"
    out_path_part = "/my/dir/path/any_filename.part"
    row = ["foo", "bar", "foobar"]

    @patch("tatoebatools.buffer.Path.iterdir")
    @patch("tatoebatools.buffer.Path.mkdir")
    def test_init_buffer(self, m_mkdir, m_iterdir):
        Buffer(self.dir, delimiter=self.delimiter, max_size=10000)

        m_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert m_iterdir.call_count == 1

    @patch("builtins.open")
    @patch("tatoebatools.buffer.Path.iterdir")
    @patch("tatoebatools.buffer.Path.mkdir")
    def test_buffer_add_below_max(self, m_mkdir, m_iterdir, m_open):
        buffer = Buffer(self.dir, delimiter=self.delimiter, max_size=10000)
        buffer.add(self.row, self.fname)

        assert buffer[self.fname] == [self.row]

    @patch("tatoebatools.buffer.csv.writer")
    @patch("builtins.open")
    @patch("tatoebatools.buffer.Path.unlink")
    @patch("tatoebatools.buffer.Path.iterdir")
    @patch("tatoebatools.buffer.Path.mkdir")
    def test_buffer_add_above_max(
        self, m_mkdir, m_iterdir, m_unlink, m_open, m_writer
    ):
        m_iterdir.return_value = set([Path(self.out_path)])  # former file
        buffer = Buffer(self.dir, delimiter=self.delimiter, max_size=0)
        buffer.add(self.row, self.fname)

        assert m_unlink.call_count == 1  # delete former file
        m_open.assert_called_once_with(Path(self.out_path_part), mode="a")
        m_writer.return_value.writerows.assert_called_once_with([self.row])
        assert buffer[self.fname] == []

    @patch("tatoebatools.buffer.Path.rename")
    @patch("tatoebatools.buffer.csv.writer")
    @patch("builtins.open")
    @patch("tatoebatools.buffer.Path.iterdir")
    @patch("tatoebatools.buffer.Path.mkdir")
    def test_buffer_clear(
        self, m_mkdir, m_iterdir, m_open, m_writer, m_rename
    ):
        buffer = Buffer(self.dir, delimiter=self.delimiter, max_size=10000)
        buffer.add(self.row, self.fname)
        buffer.clear()

        m_open.assert_called_once_with(Path(self.out_path_part), mode="a")
        m_writer.return_value.writerows.assert_called_once_with([self.row])
        m_rename.assert_called_once_with(Path(self.out_path))
