from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from tatoebatools import ParallelCorpus, tatoeba
from tatoebatools.exceptions import NotLanguage, NotLanguagePair
from tatoebatools.models import Base

data_dir = TemporaryDirectory()
tatoeba.dir = data_dir.name


@pytest.fixture
def engine():
    db_path = Path(data_dir.name).joinpath("tatoeba.sqlite")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)

    yield engine


class TestIterators:
    def test_all_tables(self):
        assert tatoeba.all_tables

    def test_all_languages(self):
        assert tatoeba.all_languages

    def test_sentences_detailed(self):
        language = "ara"
        sentences = [s for s in tatoeba.sentences_detailed(language)]

        assert sentences
        assert all(s.lang == language for s in sentences)
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

    def test_sentences_base(self):
        language = "epo"
        bases = [b for b in tatoeba.sentences_base(language)]

        assert bases
        assert all(isinstance(b.sentence_id, int) for b in bases)
        assert all(
            b.base_of_the_sentence is None
            or isinstance(b.base_of_the_sentence, int)
            for b in bases
        )

    def test_sentences_CC0(self):
        language = "eng"
        sentences = [s for s in tatoeba.sentences_CC0(language)]

        assert sentences
        assert all(isinstance(s.sentence_id, int) for s in sentences)
        assert all(s.lang == language for s in sentences)
        assert all(isinstance(s.text, str) for s in sentences)
        assert all(
            s.date_last_modified is None
            or isinstance(s.date_last_modified, datetime)
            for s in sentences
        )

    def test_links(self):
        src_lang, tgt_lang = ("swe", "fra")
        links = [lk for lk in tatoeba.links(src_lang, tgt_lang)]

        assert links
        assert all(isinstance(lk.sentence_id, int) for lk in links)
        assert all(isinstance(lk.translation_id, int) for lk in links)

    def test_tags(self):
        language = "fra"
        tags = [tg for tg in tatoeba.tags(language)]

        assert tags
        assert all(isinstance(tg.sentence_id, int) for tg in tags)
        assert all(isinstance(tg.tag_name, str) for tg in tags)

    def test_sentences_in_lists(self):
        language = "deu"
        sentences = [s for s in tatoeba.sentences_in_lists(language)]

        assert sentences
        assert all(isinstance(s.list_id, int) for s in sentences)
        assert all(isinstance(s.sentence_id, int) for s in sentences)

    def test_jpn_indices(self):
        indices = [i for i in tatoeba.jpn_indices()]

        assert indices
        assert all(isinstance(i.sentence_id, int) for i in indices)
        assert all(isinstance(i.meaning_id, int) for i in indices)
        assert all(isinstance(i.text, str) for i in indices)

    def test_sentences_with_audio(self):
        language = "spa"
        sentences = [s for s in tatoeba.sentences_with_audio(language)]

        assert sentences
        assert all(isinstance(s.sentence_id, int) for s in sentences)
        assert all(isinstance(s.audio_id, int) for s in sentences)
        assert all(isinstance(s.username, str) for s in sentences)
        assert all(
            s.license is None or isinstance(s.license, str) for s in sentences
        )
        assert all(
            s.attribution_url is None or isinstance(s.attribution_url, str)
            for s in sentences
        )

    def test_user_languages(self):
        language = "pol"
        user_languages = [ul for ul in tatoeba.user_languages(language)]

        assert user_languages
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

    def test_transcriptions(self):
        language = "jpn"
        transcriptions = [t for t in tatoeba.transcriptions(language)]

        assert transcriptions
        assert all(isinstance(t.sentence_id, int) for t in transcriptions)
        assert all(isinstance(t.lang, str) for t in transcriptions)
        assert all(isinstance(t.script_name, str) for t in transcriptions)
        assert all(isinstance(t.username, str) for t in transcriptions)
        assert all(isinstance(t.transcription, str) for t in transcriptions)

    def test_user_lists(self):
        user_lists = [ul for ul in tatoeba.user_lists()]

        assert user_lists
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

    def test_queries(self):
        language = "ces"
        queries = [q for q in tatoeba.queries(language)]

        assert queries
        assert all(q.date is None or isinstance(q.date, date) for q in queries)
        assert all(isinstance(q.language, str) for q in queries)
        assert all(isinstance(q.content, str) for q in queries)

    @pytest.mark.parametrize(
        "one_lang_table_name",
        [
            "queries",
            "sentences_CC0",
            "sentences_base",
            "sentences_detailed",
            "sentences_in_lists",
            "sentences_with_audio",
            "tags",
            "transcriptions",
            "user_languages",
        ],
    )
    def test_asterisk(self, one_lang_table_name):
        iter_table = getattr(tatoeba, one_lang_table_name)("*")

        assert next(iter_table)

    def test_asterisk_in_pair(self):
        language = "pes"
        links_1 = [lk for lk in tatoeba.links("*", language)]
        links_2 = [lk for lk in tatoeba.links(language, "*")]
        all_links = [lk for lk in tatoeba.links("*", "*")]

        assert len(links_1) == len(links_2)
        assert len(links_1) < len(all_links)

    def test_asterisk_pair(self):
        assert [lk for lk in tatoeba.links("*", "*")]

    def test_wrong_language(self):
        with pytest.raises(NotLanguage):
            [s for s in tatoeba.sentences_detailed("foobar")]

    def test_wrong_language_pair(self):
        with pytest.raises(NotLanguagePair):
            [s for s in tatoeba.links("foo", "bar")]


class TestDataFrame:
    @pytest.mark.parametrize(
        "table_name, language",
        [
            ("jpn_indices", ["*"]),
            ("links", ["deu", "fra"]),
            ("queries", ["pes"]),
            ("sentences_CC0", ["tur"]),
            ("sentences_base", ["fin"]),
            ("sentences_detailed", ["kor"]),
            ("sentences_in_lists", ["bul"]),
            ("sentences_with_audio", ["por"]),
            ("tags", ["rus"]),
            ("transcriptions", ["jpn"]),
            ("user_languages", ["kab"]),
            ("user_lists", ["ukr"]),
        ],
    )
    def test_tatoeba_get_dataframe(self, table_name, language):
        dframe = tatoeba.get(table_name, language)

        assert isinstance(dframe, pd.DataFrame)


class TestParallelCorpus:
    @pytest.mark.parametrize(
        "source_language, target_language",
        [
            ("eng", "fra"),
            ("*", "deu"),
            ("swe", "*"),
        ],
    )
    def test_parallel_corpus(self, source_language, target_language):
        parallel_corpus = [
            (s1.text, s2.text)
            for s1, s2 in ParallelCorpus(source_language, target_language)
        ]
        assert parallel_corpus


class TestDatabase:
    @pytest.mark.parametrize("table_name", tatoeba.all_tables)
    def test_ingestion(self, table_name, engine):
        def ingest(table_name, engine):
            lang = ["*", "*"] if table_name == "links" else ["*"]
            with tatoeba.get(table_name, lang, chunksize=100000) as reader:
                for chunk in reader:
                    chunk.to_sql(
                        table_name, con=engine, index=False, if_exists="append"
                    )

        ingest(table_name, engine)
        assert engine.execute(text(f"SELECT * FROM {table_name}")).fetchone()
