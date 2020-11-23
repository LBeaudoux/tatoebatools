import random
from datetime import date, datetime
from tempfile import TemporaryDirectory

from pytest import fixture, raises

from tatoebatools import tatoeba
from tatoebatools.exceptions import NotLanguage, NotLanguagePair

data_dir = TemporaryDirectory()
tatoeba.dir = data_dir.name


@fixture()
def languages():
    yield tatoeba.all_languages


@fixture()
def tables():
    yield tatoeba.all_tables


class TestTatoeba:
    def test_all_tables(self, tables):
        assert tables

    def test_all_languages(self, languages):
        assert languages

    def test_sentences_detailed(self, tables, languages):
        sentences = []
        while not sentences:
            lg = random.choice(languages)
            sentences = [s for s in tatoeba.sentences_detailed(lg)]

        assert all(s.lang == lg for s in sentences)
        assert all(isinstance(s.sentence_id, int) for s in sentences)
        assert all(isinstance(s.text, str) for s in sentences)
        assert all(
            s.username is None or isinstance(s.username, str)
            for s in sentences
        )
        assert all(
            s.date_added is None or isinstance(s.date_added, datetime)
            for s in sentences
        )
        assert all(
            s.date_last_modified is None
            or isinstance(s.date_last_modified, datetime)
            for s in sentences
        )

    def test_sentences_base(self, tables, languages):
        bases = []
        while not bases:
            lg = random.choice(languages)
            bases = [b for b in tatoeba.sentences_base(lg)]

        assert all(isinstance(b.sentence_id, int) for b in bases)
        assert all(
            b.base_of_the_sentence is None
            or isinstance(b.base_of_the_sentence, int)
            for b in bases
        )

    def test_sentences_CC0(self, tables, languages):
        sentences = []
        while not sentences:
            lg = random.choice(languages)
            sentences = [s for s in tatoeba.sentences_CC0(lg)]

        assert all(isinstance(s.sentence_id, int) for s in sentences)
        assert all(s.lang == lg for s in sentences)
        assert all(isinstance(s.text, str) for s in sentences)
        assert all(
            s.date_last_modified is None
            or isinstance(s.date_last_modified, datetime)
            for s in sentences
        )

    def test_links(self, tables, languages):
        links = []
        while not links:
            src_lg = random.choice(languages)
            tgt_lg = random.choice(languages)
            links = [lk for lk in tatoeba.links(src_lg, tgt_lg)]

        assert all(isinstance(lk.sentence_id, int) for lk in links)
        assert all(isinstance(lk.translation_id, int) for lk in links)

    def test_tags(self, tables, languages):
        tags = []
        while not tags:
            lg = random.choice(languages)
            tags = [tg for tg in tatoeba.tags(lg)]

        assert all(isinstance(tg.sentence_id, int) for tg in tags)
        assert all(isinstance(tg.tag_name, str) for tg in tags)

    def test_sentences_in_lists(self, tables, languages):
        sentences = []
        while not sentences:
            lg = random.choice(languages)
            sentences = [s for s in tatoeba.sentences_in_lists(lg)]

        assert all(isinstance(s.list_id, int) for s in sentences)
        assert all(isinstance(s.sentence_id, int) for s in sentences)

    def test_jpn_indices(self, tables):
        indices = [i for i in tatoeba.jpn_indices()]

        assert indices
        assert all(isinstance(i.sentence_id, int) for i in indices)
        assert all(isinstance(i.meaning_id, int) for i in indices)
        assert all(isinstance(i.text, str) for i in indices)

    def test_sentences_with_audio(self, tables, languages):
        sentences = []
        while not sentences:
            lg = random.choice(languages)
            sentences = [s for s in tatoeba.sentences_with_audio(lg)]

        assert all(isinstance(s.sentence_id, int) for s in sentences)
        assert all(isinstance(s.username, str) for s in sentences)
        assert all(
            s.license is None or isinstance(s.license, str) for s in sentences
        )
        assert all(isinstance(s.attribution_url, str) for s in sentences)

    def test_user_languages(self, tables, languages):
        user_languages = []
        while not user_languages:
            lg = random.choice(languages)
            user_languages = [ul for ul in tatoeba.user_languages(lg)]

        assert all(isinstance(ul.lang, str) for ul in user_languages)
        assert all(
            ul.skill_level is None or isinstance(ul.skill_level, int)
            for ul in user_languages
        )
        assert all(
            ul.username is None or isinstance(ul.username, str)
            for ul in user_languages
        )
        assert all(isinstance(ul.details, str) for ul in user_languages)

    def test_transcriptions(self, tables, languages):
        transcriptions = []
        while not transcriptions:
            lg = random.choice(languages)
            transcriptions = [t for t in tatoeba.transcriptions(lg)]

        assert all(isinstance(t.sentence_id, int) for t in transcriptions)
        assert all(isinstance(t.lang, str) for t in transcriptions)
        assert all(isinstance(t.script_name, str) for t in transcriptions)
        assert all(isinstance(t.username, str) for t in transcriptions)
        assert all(isinstance(t.transcription, str) for t in transcriptions)

    def test_user_lists(self, tables):
        user_lists = [ul for ul in tatoeba.user_lists()]

        assert all(isinstance(ul.list_id, int) for ul in user_lists)
        assert all(isinstance(ul.username, str) for ul in user_lists)
        assert all(
            ul.date_created is None or isinstance(ul.date_created, datetime)
            for ul in user_lists
        )
        assert all(
            ul.date_last_modified is None
            or isinstance(ul.date_last_modified, datetime)
            for ul in user_lists
        )
        assert all(isinstance(ul.list_name, str) for ul in user_lists)
        assert all(isinstance(ul.editable_by, str) for ul in user_lists)

    def test_queries(self, tables, languages):
        queries = []
        while not queries:
            lg = random.choice(languages)
            queries = [q for q in tatoeba.queries(lg)]

        assert all(q.date is None or isinstance(q.date, date) for q in queries)
        assert all(isinstance(q.language, str) for q in queries)
        assert all(isinstance(q.content, str) for q in queries)

    def test_asterisk(self, tables):
        one_lang_tables = set(tables) - {"links", "user_lists", "jpn_indices"}
        tbl_name = random.choice(list(one_lang_tables))

        tbl_items = [x for x in getattr(tatoeba, tbl_name)("*")]

        assert tbl_items

    def test_asterisk_in_pair(self, languages):
        lg = random.choice(languages)
        links_1 = []
        links_2 = []
        while not links_1:
            links_1 = [lk for lk in tatoeba.links("*", lg)]
            links_2 = [lk for lk in tatoeba.links(lg, "*")]
        all_links = [lk for lk in tatoeba.links("*", "*")]

        assert len(links_1) == len(links_2)
        assert len(links_1) < len(all_links)

    def test_asterisk_pair(self):
        assert [lk for lk in tatoeba.links("*", "*")]

    def test_wrong_language(self):
        with raises(NotLanguage):
            [s for s in tatoeba.sentences_detailed("foobar")]

    def test_wrong_language_pair(self):
        with raises(NotLanguagePair):
            [s for s in tatoeba.links("foo", "bar")]
