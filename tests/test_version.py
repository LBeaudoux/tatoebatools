from datetime import datetime
from unittest.mock import patch

import pytest

from tatoebatools.version import Version


class TestVersion:
    @patch("tatoebatools.version.json.load")
    @patch("builtins.open")
    def test_init_with_file(self, m_open, m_load):
        m_load.return_value = {"foo": "2020-05-22 11:51:00"}
        version = Version()

        assert m_open.call_count == 1
        assert m_load.call_count == 1
        assert len(version) == 1

    @patch("builtins.open")
    def test_init_without_file(self, m_open):
        m_open.side_effect = FileNotFoundError
        version = Version()

        assert m_open.call_count == 1
        assert len(version) == 0

    @patch("tatoebatools.version.json.load")
    @patch("builtins.open")
    def test_item_getter_with_file(self, m_open, m_load):
        m_load.return_value = {"foo": "2020-05-22 11:51:00"}
        version = Version()

        assert version["foo"] == datetime(2020, 5, 22, 11, 51, 0)
        assert version["bar"] is None

    @patch("tatoebatools.version.json.dump")
    @patch("tatoebatools.version.json.load")
    @patch("builtins.open")
    def test_item_setter(self, m_open, m_load, m_dump):
        m_load.return_value = {"foo": "2000-01-01 00:00:00"}
        version = Version()

        # set version with a datetime instance
        version["foobar"] = datetime(2020, 5, 22, 23, 51, 0)
        assert m_open.call_count == 2
        assert m_dump.call_count == 1
        assert m_dump.call_args[0][0] == {
            "foobar": "2020-05-22 23:51:00",
            "foo": "2000-01-01 00:00:00",
        }

        # replace a version
        version["foo"] = datetime(2019, 11, 3, 0, 0, 0)
        assert m_open.call_count == 3
        assert m_dump.call_count == 2
        assert m_dump.call_args[0][0] == {
            "foobar": "2020-05-22 23:51:00",
            "foo": "2019-11-03 00:00:00",
        }

        # set version with string instead of datetime instance
        with pytest.raises(AttributeError):
            version["foobar"] = "foobar"
