from pytest import raises

from tatoebatools.exceptions import NotLanguagePair
from tatoebatools.update import _get_urls_to_check


class TestGetURLsToCheck:
    def test_monolingual_tables(self):

        tables = [
            "sentences_base",
            "sentences_CC0",
            "sentences_detailed",
            "sentences_in_lists",
            "sentences_with_audio",
            "tags",
            "transcriptions",
            "user_languages",
        ]
        language_codes = ["eng"]
        for tbl in tables:
            for oriented_pair in (True, False):
                assert _get_urls_to_check(
                    [tbl], language_codes, oriented_pair
                ) == {
                    f"https://downloads.tatoeba.org/exports/per_language/eng/"
                    f"eng_{tbl}.tsv.bz2"
                }

    def test_no_language_tables(self):

        tables = ["jpn_indices", "user_lists"]
        language_codes = []
        for tbl in tables:
            for oriented_pair in (True, False):
                assert _get_urls_to_check(
                    [tbl], language_codes, oriented_pair
                ) == {
                    f"https://downloads.tatoeba.org/exports/" f"{tbl}.tar.bz2"
                }

    def test_links(self):

        table = ["links"]
        language_codes = ["eng", "fra"]

        assert _get_urls_to_check(
            table, language_codes, oriented_pair=True
        ) == {
            "https://downloads.tatoeba.org/exports/per_language/eng/"
            "eng-fra_links.tsv.bz2"
        }

        assert _get_urls_to_check(
            table, language_codes, oriented_pair=False
        ) == {
            "https://downloads.tatoeba.org/exports/per_language/eng/"
            "eng-fra_links.tsv.bz2",
            "https://downloads.tatoeba.org/exports/per_language/eng/"
            "eng-eng_links.tsv.bz2",
            "https://downloads.tatoeba.org/exports/per_language/fra/"
            "fra-fra_links.tsv.bz2",
            "https://downloads.tatoeba.org/exports/per_language/fra/"
            "fra-eng_links.tsv.bz2",
        }

    def test_queries(self):

        table = ["queries"]
        language_codes = ["eng", "fra"]
        for oriented_pair in (True, False):
            assert _get_urls_to_check(
                table, language_codes, oriented_pair
            ) == {"https://downloads.tatoeba.org/stats/" "queries.csv.bz2"}

    def test_update_with_empty_args(self):
        for oriented_pair in (True, False):
            assert _get_urls_to_check([], [], oriented_pair) == set()

    def test_update_with_not_language_pair(self):
        table_names = ["links"]
        language_codes = ["eng", "fra", "deu"]
        with raises(NotLanguagePair):
            _get_urls_to_check(table_names, language_codes, oriented_pair=True)
