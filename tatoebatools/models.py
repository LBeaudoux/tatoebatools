from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JpnIndex(Base):

    __tablename__ = "jpn_indices"

    id = Column(Integer, autoincrement=True, primary_key=True)
    sentence_id = Column(Integer)
    meaning_id = Column(Integer)
    text = Column(String(2000), nullable=True)


class Link(Base):

    __tablename__ = "links"

    sentence_id = Column(Integer, primary_key=True)
    translation_id = Column(Integer, primary_key=True)


class SentenceBase(Base):

    __tablename__ = "sentences_base"

    sentence_id = Column(Integer, primary_key=True)
    base_of_the_sentence = Column(Integer, nullable=True)


class SentenceCC0(Base):

    __tablename__ = "sentences_CC0"

    sentence_id = Column(Integer, primary_key=True)
    lang = Column(String(4), nullable=True)
    text = Column(String(1500), nullable=False)
    date_last_modified = Column(DateTime, nullable=True)


class SentenceDetailed(Base):

    __tablename__ = "sentences_detailed"

    sentence_id = Column(Integer, primary_key=True)
    lang = Column(String(4), nullable=True)
    text = Column(String(1500))
    username = Column(String(20), nullable=True)
    date_added = Column(DateTime, nullable=True)
    date_last_modified = Column(DateTime, nullable=True)


class SentenceInList(Base):

    __tablename__ = "sentences_in_lists"

    list_id = Column(Integer, primary_key=True)
    sentence_id = Column(Integer, primary_key=True)


class SentenceWithAudio(Base):

    __tablename__ = "sentences_with_audio"

    id = Column(Integer, autoincrement=True, primary_key=True)
    sentence_id = Column(Integer)
    audio_id = Column(Integer)
    username = Column(String(20), nullable=True)
    license = Column(String(50), nullable=True)
    attribution_url = Column(String(255), nullable=True)


class Tag(Base):

    __tablename__ = "tags"

    sentence_id = Column(Integer, primary_key=True)
    tag_name = Column(String(50), primary_key=True)


class Queries(Base):

    __tablename__ = "queries"

    id = Column(Integer, autoincrement=True, primary_key=True)
    date = Column(DateTime)
    language = Column(String(4), nullable=True)
    content = Column(Text)


class Transcription(Base):

    __tablename__ = "transcriptions"

    sentence_id = Column(Integer, primary_key=True)
    lang = Column(String(4), nullable=True)
    script_name = Column(String(4), primary_key=True)
    username = Column(String(20), nullable=True)
    transcription = Column(String(10000))


class UserLanguage(Base):

    __tablename__ = "user_languages"

    lang = Column(String(4), nullable=True, primary_key=True)
    skill_level = Column(Integer, nullable=True)
    username = Column(String(20), nullable=True, primary_key=True)
    details = Column(Text, nullable=True)


class UserList(Base):

    __tablename__ = "user_lists"

    list_id = Column(Integer, primary_key=True)
    username = Column(String(20))
    date_created = Column(DateTime, nullable=True)
    date_last_modified = Column(DateTime, nullable=True)
    list_name = Column(String(450))
    editable_by = Column(String(7))
