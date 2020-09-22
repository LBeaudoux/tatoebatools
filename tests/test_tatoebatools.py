from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from pytest import raises

from tatoebatools.exceptions import (
    NotAvailableLanguage,
    NotAvailableTable,
    NotLanguagePair,
)
from tatoebatools.tatoebatools import Tatoeba


class TestTatoeba:
    @patch("tatoebatools.tatoebatools.DataFile.find_changes")
    @patch("tatoebatools.tatoebatools.Table.classify")
    @patch("tatoebatools.tatoebatools.Table.index")
    @patch("tatoebatools.tatoebatools.Download.fetch")
    @patch("tatoebatools.tatoebatools.check_updates")
    def test_update_sentences_detailed(
        self, m_check, m_fetch, m_index, m_classify, m_find_changes
    ):
        table_names = ["sentences_detailed"]
        language_codes = ["eng", "fra"]
        m_check.return_value = {"any_url": datetime(2020, 4, 2, 20, 52, 42)}
        m_fetch.return_value = [Path("/any/path/abc_sentences_detailed.tsv")]
        Tatoeba().update(table_names, language_codes)

        m_check.assert_called_once_with(
            table_names, language_codes, oriented_pair=False, verbose=True
        )
        assert m_fetch.call_count == 1
        assert m_index.call_count == 0
        assert m_classify.call_count == 0
        assert m_find_changes.call_count == 1

    @patch("tatoebatools.tatoebatools.DataFile.find_changes")
    @patch("tatoebatools.tatoebatools.Table.classify")
    @patch("tatoebatools.tatoebatools.Table.index")
    @patch("tatoebatools.tatoebatools.Download.fetch")
    @patch("tatoebatools.tatoebatools.check_updates")
    def test_update_links(
        self, m_check, m_fetch, m_index, m_classify, m_find_changes
    ):
        table_names = ["links"]
        language_codes = ["eng", "fra"]
        m_check.return_value = {"any_url": datetime(2020, 4, 2, 20, 52, 42)}
        m_fetch.return_value = [Path("/any/path/abc_sentences_detailed.tsv")]
        Tatoeba().update(table_names, language_codes, oriented_pair=True)

        m_check.assert_called_once_with(
            table_names, language_codes, oriented_pair=True, verbose=True
        )
        assert m_fetch.call_count == 1
        assert m_index.call_count == 0
        assert m_classify.call_count == 0
        assert m_find_changes.call_count == 1

    @patch("tatoebatools.tatoebatools.DataFile.find_changes")
    @patch("tatoebatools.tatoebatools.Table.classify")
    @patch("tatoebatools.tatoebatools.Table.index")
    @patch("tatoebatools.tatoebatools.Download.fetch")
    @patch("tatoebatools.tatoebatools.check_updates")
    def test_update_queries(
        self, m_check, m_fetch, m_index, m_classify, m_find_changes
    ):
        table_names = ["queries"]
        language_codes = []
        m_check.return_value = {"any_url": datetime(2020, 4, 2, 20, 52, 42)}
        m_fetch.return_value = [Path("/any/path/queries.csv")]
        Tatoeba().update(table_names, language_codes)

        m_check.assert_called_once_with(
            table_names, language_codes, oriented_pair=False, verbose=True
        )
        assert m_fetch.call_count == 1
        assert m_index.call_count == 0
        assert m_classify.call_count == 1
        assert m_find_changes.call_count == 0

    @patch("tatoebatools.tatoebatools.check_updates", return_value={})
    def test_update_up_to_date(self, m_check_updates):
        table_names = ["sentences_detailed", "links"]
        language_codes = ["eng", "fra"]

        Tatoeba().update(table_names, language_codes)
        m_check_updates.assert_called_once_with(
            table_names, language_codes, oriented_pair=False, verbose=True
        )

    def test_update_with_empty_args(self):
        assert Tatoeba().update(table_names=[], language_codes=[]) is None

    def test_update_with_not_available_table(self):
        table_names = ["foobar"]
        language_codes = []
        with raises(NotAvailableTable):
            Tatoeba().update(table_names, language_codes)

    def test_update_with_not_available_language(self):
        table_names = []
        language_codes = ["foobar"]
        with raises(NotAvailableLanguage):
            Tatoeba().update(table_names, language_codes)

    def test_update_with_not_language_pair(self):
        table_names = ["links"]
        language_codes = ["eng", "fra", "deu"]
        with raises(NotLanguagePair):
            Tatoeba().update(table_names, language_codes, oriented_pair=True)
