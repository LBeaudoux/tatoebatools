from datetime import datetime
from unittest.mock import patch

from tatoebatools.version import Version, json


@patch.object(json, "load", return_value={"foobar": "2020-05-22 11:51:00"})
@patch("builtins.open")
def test_version_item_getter(mock_open, mock_load):
    dt = datetime(year=2020, month=5, day=22, hour=11, minute=51, second=00)
    dt_sting = "2020-05-22 11:51:00"

    version = Version()
    mock_open.assert_called_once()
    mock_load.assert_called_once()
    assert version._dict == {"foobar": dt_sting}
    assert version["foobar"] == dt


@patch.object(json, "dump")
@patch.object(json, "load", return_value={"foo": "2000-01-01 00:00:00"})
@patch("builtins.open")
def test_version_item_setter(mock_open, mock_load, mock_dump):
    dt = datetime(year=2020, month=5, day=22, hour=11, minute=51, second=00)
    dt_string = "2020-05-22 11:51:00"

    version = Version()
    d0 = version._dict
    assert d0 == {"foo": "2000-01-01 00:00:00"}

    version["foobar"] = dt
    d1 = version._dict
    assert d1 == {**d0, **{"foobar": dt_string}}

    assert mock_open.call_count == 2
    mock_load.assert_called_once()
    assert mock_dump.call_args[0][0] == d1
