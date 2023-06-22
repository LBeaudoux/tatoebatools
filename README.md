# tatoebatools

[![Actions Status](https://github.com/LBeaudoux/tatoebatools/workflows/CI/badge.svg)](https://github.com/LBeaudoux/tatoebatools/actions?query=workflow%3ACI)


**tatoebatools** helps you to integrate [Tatoeba](https://tatoeba.org) into your app more quickly by allowing you to easily download and parse [Tatoeba weekly exports](https://downloads.tatoeba.org/exports/).

## Installation

This library supports Python 3.8+.

```sh
pip install tatoebatools
```

## Basic Usage

Use the high-level `ParallelCorpus` class to automatically download and iterate through all sentence/translation pairs from a source language to a target language.

```python
>>> from tatoebatools import ParallelCorpus
>>> for sentence, translation in ParallelCorpus("cmn", "eng"):
        print((sentence.text, translation.text))
...
('那里有八块小圆石。', 'There were eight pebbles there.')
('这个椅子坐着不舒服。', 'This chair is uncomfortable.')
('我会在这里等着到他回来的。', 'Until he comes back, I will wait here.')
```

## Advanced Usage

The Tatoeba data files are handled by the `tatoeba` object.

```python
from tatoebatools import tatoeba
```

By default, the fetched Tatoeba data files are stored inside the **tatoebatools** package. But you can download them to another location.

```python
tatoeba.dir = "/path/to/my/tatoeba/dir"
```

Use the `all_tables` attribute to list the Tatoeba data tables you can have access
to.

```python
>>> tatoeba.all_tables
['jpn_indices', 'links', ... , 'user_languages', 'user_lists']
```

Each table has its own set of attributes:

|Table               |Attributes                                                                 |
|--------------------|---------------------------------------------------------------------------|
|sentences_detailed  |sentence_id, lang, text, username, date_added, date_last_modified          |
|sentences_base      |sentence_id, base_of_the_sentence                                          |
|sentences_CC0       |sentence_id, lang, text, date_last_modified                                |
|links               |sentence_id, translation_id                                                |
|tags                |sentence_id, tag_name                                                      |
|sentences_in_lists  |list_id, sentence_id                                                       |
|jpn_indices         |sentence_id, meaning_id, text                                              |
|sentences_with_audio|sentence_id, audio_id, username, license, attribution_url                            |
|user_languages      |lang, skill_level, username, details                                       |
|transcriptions      |sentence_id, lang, script_name, username, transcription                    |
|user_lists          |list_id, username, date_created, date_last_modified, list_name, editable_by|

Find out more about the Tatoeba data files and their fields [here](https://tatoeba.org/eng/downloads).

Most Tatoeba languages are identified by their [IS0 639-3 codes](https://iso639-3.sil.org/code_tables/639/data). The asterisk character '*' designates all languages supported by Tatoeba. Call the `all_languages` attribute to list the languages supported by Tatoeba.

```python
>>> tatoeba.all_languages
['abk', 'acm', ... , 'zul', 'zza']
```

### Reading Tatoeba data with iterators

To read a table, just call its iterator. The downloading of the data file will be automatically handled in the background.

Set the `scope` argument to 'added' to only read rows that did not exist in the previous local version of an updated file. Set it to 'removed' to iterate over the rows that don't exist anymore.

```python
# list all sentences in English
english_texts = [s.text for s in tatoeba.sentences_detailed("eng")]

# list all German sentences that were added by the latest local update
new_german_texts = [s.text for s in tatoeba.sentences_detailed("deu", scope="added")]

# list all links between French and Italian sentences
french_italian_links = [(lk.sentence_id, lk.translation_id) for lk in tatoeba.links("fra", "ita")]

# list all French native speakers
native_french = [x.username for x in tatoeba.user_languages("fra") if x.skill_level == 5]

# map German sentences to their audios
german_audios = {}
for audio in tatoeba.sentences_with_audio("deu"):
    german_audios.setdefault(audio.sentence_id, []).append(audio.audio_id)
```

### Extracting Tatoeba data as dataframe

Since **tatoebatools** relies heavily on the [pandas](https://github.com/pandas-dev/pandas) library, it is possible to load any supported table into memory as a dataframe.

```python
# get the dataframe of the English sentences table
english_sentences_dataframe = tatoeba.get("sentences_detailed", ["eng"])

# get the dataframe of all links for which French is the source language
french_links_dataframe = tatoeba.get("links", ["fra", "*"])
```

### Ingesting Tatoeba data into a database

The **tatoebatools** library includes [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) models that help you to ingest Tatoeba data in the database of you choice. 

In the example below, all sentence and user data is loaded into a local SQLite database, and then an index is added to speed up database queries.

```python
from sqlalchemy import create_engine, Index

from tatoebatools import tatoeba
from tatoebatools.models import Base, SentenceDetailed

engine = create_engine( "sqlite:///./tatoeba.sqlite")

table_names = ["sentences_detailed", "user_languages"]

# create the tables in the database
tables = [
    Base.metadata.tables[table_name] 
    for table_name in table_names
]
Base.metadata.create_all(bind=engine, tables=tables)

# insert data into the tables
for table_name in table_names:
    with tatoeba.get(table_name, ["*"], chunksize=100000) as reader:
        for chunk in reader:
            chunk.to_sql(table_name, con=engine, index=False, if_exists="append")

# add an index on the 'username' column of the 'sentences_detailed' table
ix = Index('ix_sentences_detailed_username', SentenceDetailed.username)
ix.create(engine)
```
