from unittest.mock import patch

from tatoebatools.index import Index


def test_index_without_int_key():
    with patch(
        "tatoebatools.datafile.DataFile", autospec=True
    ) as MockDataFile:
        table = [["42", "fra", "foobar"], ["123", "eng", "barfoo"]]
        MockDataFile.return_value.__iter__.return_value = iter(table)

        df = MockDataFile("any_file_path")
        dict_ind = {k: v for k, v in Index(df, 0, 1)}

        assert dict_ind == {"42": "fra", "123": "eng"}


def test_index_with_int_key():
    with patch(
        "tatoebatools.datafile.DataFile", autospec=True
    ) as MockDataFile:
        table = [["42", "fra", "foobar"], ["123", "eng", "barfoo"]]
        MockDataFile.return_value.__iter__.return_value = iter(table)

        df = MockDataFile("any_file_path")
        dict_ind = {k: v for k, v in Index(df, 0, 1, int_key=True)}

        assert dict_ind == {42: "fra", 123: "eng"}
