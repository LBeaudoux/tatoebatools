Tatoeba Tools
=============

By allowing you to easily download and parse monolingual data files, *tatoebatools* helps you to integrate `Tatoeba <https://tatoeba.org>`_ into your codebase more quickly.


Installation
------------

This library requires Python 3.6

.. code:: sh

    pip3 install tatoebatools


Basic Usage
-----------

Use the high-level *ParallelCorpus* class to automatically download and iterate over all sentence/translation pairs from a source language to a target language.

.. code-block:: python

    >>> from tatoebatools import ParallelCorpus
    >>> for sentence, translation in ParallelCorpus("cmn", "eng"):
            print((sentence.text, translation.text))
    ...
    ('那里有八块小圆石。', 'There were eight pebbles there.')
    ('这个椅子坐着不舒服。', 'This chair is uncomfortable.')
    ('我会在这里等着到他回来的。', 'Until he comes back, I will wait here.')


Advanced Usage
--------------

The data files are handled by the *tatoeba* object.

.. code-block:: python

    >>> from tatoebatools import tatoeba


Use the *all_tables* attribute to list the tables you can have access to:

.. code-block:: python

    >>> tatoeba.all_tables
    ['jpn_indices', 'links', ... , 'user_languages', 'user_lists']

Each table has its own set of attributes:

+----------------------+-------------------------------+
| Table                | Attributes                    |
+======================+===============================+
| sentences_detailed   | sentence_id, lang, text,      |
|                      | username, date_added,         |
|                      | date_last_modified            |
+----------------------+-------------------------------+
| sentences_base       | sentence_id,                  |
|                      | base_of_the_sentence          |
+----------------------+-------------------------------+
| sentences_CC0        | sentence_id, lang, text,      |
|                      | date_last_modified            |
+----------------------+-------------------------------+
| links                | sentence_id, translation_id   |
+----------------------+-------------------------------+
| tags                 | sentence_id, tag_name         |
+----------------------+-------------------------------+
| sentences_in_lists   | list_id, sentence_id          |
+----------------------+-------------------------------+
| jpn_indices          | sentence_id, meaning_id, text |
+----------------------+-------------------------------+
| sentences_with_audio | sentence_id, username,        |
|                      | license, attribution_url      |
+----------------------+-------------------------------+
| user_languages       | lang, skill_level, username,  |
|                      | details                       |
+----------------------+-------------------------------+
| transcriptions       | sentence_id, lang,            |
|                      | script_name, username,        |
|                      | transcription                 |
+----------------------+-------------------------------+
| user_lists           | list_id, username,            |
|                      | date_created,                 |
|                      | date_last_modified,           |
|                      | list_name, editable_by        |
+----------------------+-------------------------------+

Find out more about the Tatoeba data files and their fields `here <https://tatoeba.org/eng/downloads>`_.



You can call *all_languages* to list the languages supported by Tatoeba:

.. code-block:: python

    >>> tatoeba.all_languages
    ['abk', 'acm', 'ady', ... , 'zsm', 'zul', 'zza']



Iterating over a table
^^^^^^^^^^^^^^^^^^^^^^
To read a table, just call its iterator. The downloading of data files will be automatically handled in the background.

Set the *scope* argument to 'added' to only read rows that did not exist in the previous version of an updated file. Set it to 'removed' to iterate over the rows that don't exist anymore.

Examples
""""""""
List all sentences in English:

.. code-block:: python

    >>> english_texts = [s.text for s in tatoeba.sentences_detailed("eng")]

List all German sentences that were added by the latest update:

.. code-block:: python

    >>> new_german_texts = [s.text for s in tatoeba.sentences_detailed("deu", scope="added")]

List all links between French and Italian sentences:

.. code-block:: python

    >>>  links = [(lk.sentence_id, lk.translation_id) for lk in tatoeba.links("fra", "ita")]

List all French native speakers:

.. code-block:: python

    >>> native_french = [x.username for x in tatoeba.user_languages("fra") if x.skill_level == 5]
