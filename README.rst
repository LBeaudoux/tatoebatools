TATOEBA TOOLS
=============

*tatoebatools* is a Python library for easily downloading and iterating over data from the Tatoeba project.


Installation
------------

This library requires Python 3.6. 

.. code:: sh

    pip3 install tatoebatools


Basic usage
-----------

Downloading and iterating over all the sentences in a language
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> from tatoebatools import Corpus

    >>> corpus = Corpus("fra")
    >>> for s in corpus:
            print((s.sentence_id, s.text, s.username))
    ...
    (8819708, 'Nous avons rendu visite à mamie hier.', 'felix63')
    (8819719, 'Elle a été percutée par une voiture.', 'Julien_PDC')
    (8819766, 'Je te tiens informé.', 'felix63')


Downloading and iterating over all sentence/translation pairs from a source language to a target language
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> from tatoebatools import ParallelCorpus

    >>> parallel_corpus = ParallelCorpus("cmn", "eng")
    >>> for sentence, translation in parallel_corpus:
            print((sentence.text, translation.text))
    ...
    ('那里有八块小圆石。', 'There were eight pebbles there.')
    ('这个椅子坐着不舒服。', 'This chair is uncomfortable.')
    ('我会在这里等着到他回来的。', 'Until he comes back, I will wait here.')


Advanced usage
--------------

Import the lower-level *tatoeba* object to enable extended features.

.. code-block:: python

    >>> from tatoebatools import tatoeba


Listing all tables that can be downloaded from tatoeba.org
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    >>> tatoeba.all_tables
    ['jpn_indices', 'links', ... , 'user_languages', 'user_lists']


Listing all languages available on Tatoeba
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> tatoeba.all_languages
    ['abk', 'acm', 'ady', ... , 'zsm', 'zul', 'zza']


Updating chosen tables for a set of languages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> tatoeba.update(["tags", "sentences_with_audio"], ["rus", "swe"])
    checking for updates on https://downloads.tatoeba.org
    100%|███████████████████████████| 2/2 [00:00<00:00,  4.35it/s]
    3 files to download
    downloading https://downloads.tatoeba.org/exports/per_language/swe/swe_tags.tsv.bz2
    100%|███████████████████████████| 16.4k/16.4k [00:00<00:00, 2.77MiB/s]
    decompressing swe_tags.tsv.bz2
    downloading https://downloads.tatoeba.org/exports/per_language/rus/rus_sentences_with_audio.tsv.bz2
    100%|███████████████████████████| 22.2k/22.2k [00:00<00:00, 3.75MiB/s]
    decompressing rus_sentences_with_audio.tsv.bz2
    ...
    tags, sentences_with_audio updated


Iterating over a table
^^^^^^^^^^^^^^^^^^^^^^

Any downloaded table is readable. 

For example, you can list all French native speakers by iterating over *user_languages*:

.. code-block:: python

    >>> native_french = [x.username for x in tatoeba.user_languages("fra") if x.skill_level == 5]

Find out more about the tables and their fields at https://tatoeba.org/eng/downloads