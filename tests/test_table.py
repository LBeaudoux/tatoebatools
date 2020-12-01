from unittest.mock import patch

from pytest import raises
from tatoebatools.exceptions import NotLanguage, NotLanguagePair, NotTable
from tatoebatools.table import Table


class TestTable:

    ok_tables = {"links", "sentences_detailed"}
    ok_languages = {"eng", "fra"}

    @patch("tatoebatools.update.Update.run")
    @patch("tatoebatools.table.check_tables", return_value=ok_tables)
    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init(self, m_check_lg, m_check_tbl, m_update):
        Table("sentences_detailed", ["fra"])
        m_check_lg.call_count == 1
        m_check_tbl.call_count == 1
        m_update.call_count == 1

    @patch("tatoebatools.update.Update.run")
    @patch("tatoebatools.table.check_tables", return_value=ok_tables)
    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_with_asterisk(self, m_check_lg, m_check_tbl, m_update):
        Table("sentences_detailed", ["*"])

    @patch("tatoebatools.update.Update.run")
    @patch("tatoebatools.table.check_tables", return_value=ok_tables)
    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_with_no_update(self, m_check_lg, m_check_tbl, m_update):
        Table("sentences_detailed", ["*"], update=False)
        m_update.call_count == 0

    @patch("tatoebatools.update.Update.run")
    @patch("tatoebatools.table.check_tables", return_value=ok_tables)
    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_links(self, m_check_lg, m_check_tbl, m_update):
        Table("links", ["fra", "eng"])

    @patch("tatoebatools.datafile.DataFile.join")
    @patch("tatoebatools.update.Update.run")
    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_links_with_one_asterisk(self, m_check_lg, m_update, m_join):
        Table("links", ["*", "eng"])
        assert m_join.call_count == 1

    @patch("tatoebatools.update.Update.run")
    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_links_with_two_asterisks(self, m_check_lg, m_update):
        Table("links", ["*", "*"])

    def test_init_with_empty_args(self):
        with raises(TypeError):
            Table()

    @patch("tatoebatools.table.check_tables", return_value=ok_tables)
    def test_init_with_not_table(self, m_check_tbl):
        with raises(NotTable):
            Table("foobar")

    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_with_not_language_1(self, m_check_lg):
        with raises(NotLanguage):
            Table("sentences_detailed", ["foobar"])

    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_with_not_language_2(self, m_check_lg):
        with raises(NotLanguage):
            Table("sentences_detailed", ["eng", "fra"])

    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_links_with_not_language_pair_1(self, m_check_lg):
        with raises(NotLanguagePair):
            Table("links", ["eng", "fra", "deu"])

    @patch("tatoebatools.table.check_languages", return_value=ok_languages)
    def test_init_links_with_not_language_pair_2(self, m_check_lg):
        with raises(NotLanguagePair):
            Table("links", ["eng"])
