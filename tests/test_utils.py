from pathlib import Path
from tarfile import ReadError
from unittest.mock import patch

from requests.exceptions import RequestException

from tatoebatools.utils import decompress, download, extract, fetch


class TestDownload:

    from_url = "https://foobar.com/myfile.tar.bz2"
    to_dir = "/this/is/my/dir"
    to_path = "/this/is/my/dir/myfile.tar.bz2"
    data = [b"B", b"Z", b"&", b"S", b"Y"]

    @patch("builtins.open")
    @patch("tatoebatools.utils.requests.get")
    @patch("tatoebatools.utils.Path.mkdir")
    def test_download_ok(self, m_mkdir, m_get, m_open):
        m_r = m_get.return_value.__enter__.return_value
        m_r.status_code = 200
        m_r.iter_content.return_value = iter(self.data)
        m_f = m_open.return_value.__enter__.return_value
        dl = download(self.from_url, self.to_dir)

        m_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        m_get.assert_called_once_with(self.from_url, stream=True)
        m_open.assert_called_once_with(Path(self.to_path), "wb")
        assert [x[0][0] for x in m_f.write.call_args_list] == self.data
        assert dl == Path(self.to_path)

    @patch("tatoebatools.utils.requests.get")
    @patch("tatoebatools.utils.Path.mkdir")
    def test_download_not_ok(self, m_mkdir, m_get):
        m_get.side_effect = RequestException
        dl = download(self.from_url, self.to_dir)

        assert m_get.call_count == 1
        assert dl is None


class TestDecompress:

    in_path = "/my/path/myfile.ext.bz2"
    out_path = "/my/path/myfile.ext"

    @patch("tatoebatools.utils.Path.unlink")
    @patch("builtins.open")
    @patch("tatoebatools.utils.bz2.open")
    def test_with_compressed_file(self, m_bz2_open, m_open, m_unlink):
        m_in_f = m_bz2_open.return_value.__enter__.return_value
        m_out_f = m_open.return_value.__enter__.return_value
        out_path = decompress(self.in_path)

        m_bz2_open.assert_called_once_with(Path(self.in_path))
        m_open.assert_called_once_with(Path(self.out_path), "wb")
        assert m_in_f.read.call_count == 1
        assert m_out_f.write.call_count == 1
        assert m_unlink.call_count == 1
        assert out_path == Path(self.out_path)

    @patch("builtins.open")
    @patch("tatoebatools.utils.bz2.open", side_effect=FileNotFoundError)
    def test_with_no_file(self, m_bz2_open, m_open):
        out_path = decompress(self.in_path)

        m_bz2_open.assert_called_once_with(Path(self.in_path))
        assert out_path is None

    @patch("builtins.open")
    @patch("tatoebatools.utils.bz2.open", side_effect=OSError)
    def test_with_not_compressed_file(self, m_bz2_open, m_open):
        out_path = decompress(self.in_path)

        m_bz2_open.assert_called_once_with(Path(self.in_path))
        assert out_path is None


class TestExtract:

    archive_path = "/my/dir/arx_filename.tar"
    out_dir = "/my/dir"
    out_filenames = ["foobar.ext", "foo.bar"]
    out_filepaths = ["/my/dir/foobar.ext", "/my/dir/foo.bar"]

    @patch("tatoebatools.utils.Path.unlink")
    @patch("tatoebatools.utils.tarfile.open")
    def test_with_archive(self, m_tar_open, m_unlink):
        m_tar = m_tar_open.return_value.__enter__.return_value
        m_tar.getnames.return_value = self.out_filenames

        out_filepaths = extract(self.archive_path)

        m_tar_open.assert_called_once_with(Path(self.archive_path))
        m_tar.extractall.assert_called_once_with(Path(self.out_dir))
        assert m_tar.getnames.call_count == 1
        assert m_unlink.call_count == 1
        assert out_filepaths == [Path(fp) for fp in self.out_filepaths]

    @patch("tatoebatools.utils.tarfile.open")
    def test_without_archive(self, m_tar_open):
        m_tar = m_tar_open.return_value.__enter__.return_value
        m_tar.extractall.side_effect = ReadError

        out_filepaths = extract(self.archive_path)

        m_tar_open.assert_called_once_with(Path(self.archive_path))
        m_tar.extractall.assert_called_once_with(Path(self.out_dir))
        assert out_filepaths == []

    @patch("tatoebatools.utils.tarfile.open", side_effect=FileNotFoundError)
    def test_without_file(self, m_tar_open):
        out_filepaths = extract(self.archive_path)

        assert out_filepaths == []


class TestFetch:
    @patch("tatoebatools.utils.extract")
    @patch("tatoebatools.utils.decompress")
    @patch("tatoebatools.utils.download")
    def test_with_tar_bz2_file(self, m_download, m_decompress, m_extract):
        m_download.return_value = Path("/mydir/file.tar.bz2")
        m_decompress.return_value = Path("/mydir/file.tar")
        m_extract.return_value = [Path("/mydir/file.ext")]

        assert fetch("any_url", "any_dir") == [Path("/mydir/file.ext")]

    @patch("tatoebatools.utils.decompress")
    @patch("tatoebatools.utils.download")
    def test_with_tsv_bz2_file(self, m_download, m_decompress):
        m_download.return_value = Path("/mydir/file.tsv.bz2")
        m_decompress.return_value = Path("/mydir/file.tsv")

        assert fetch("any_url", "any_dir") == [Path("/mydir/file.tsv")]

    @patch("tatoebatools.utils.download")
    def test_with_csv_file(self, m_download):
        m_download.return_value = Path("/mydir/file.csv")

        assert fetch("any_url", "any_dir") == [Path("/mydir/file.csv")]

    @patch("tatoebatools.utils.download")
    def test_with_failed_download(self, m_download):
        m_download.return_value = None

        assert fetch("any_url", "any_dir") == []
