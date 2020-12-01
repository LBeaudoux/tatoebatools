Tatoeba Tools
=============

By allowing you to easily download and parse data files, *tatoebatools* helps you to integrate `Tatoeba <https://tatoeba.org>`_ into your codebase more quickly.



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

By default, the data files are stored inside the *tatoebatools* library. But you can download them to another location.

.. code-block:: python

    >>> tatoeba.dir = "/path/to/my/tatoeba/dir"

Use the *all_tables* attribute to list the tables you can have access to.

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

Languages are identified by their IS0 639-3 codes. The asterisk character '*' designates all languages supported by Tatoeba. Call the *all_languages* attribute to list the languages supported by Tatoeba.

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
    
    
Get the dataframe of a table
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Since *tatoebatools* relies heavily on pandas, it is also possible to directly get the dataframe of any supported table.

Examples
""""""""
Get the dataframe of the English sentences table:

.. code-block:: python

    >>> tatoeba.get("sentences_detailed", ["eng"])
    
                lang                                               text   username          date_added  date_last_modified
    sentence_id                                                                                                           
    1276         eng                               Let's try something.         CK                 NaT 2012-02-05 11:38:18
    1277         eng                             I have to go to sleep.     vinhan                 NaT 2009-11-25 23:20:59
    1280         eng   Today is June 18th and it is Muiriel's birthday!     wuiwie                 NaT 2019-03-24 11:45:41
    1282         eng                                 Muiriel is 20 now.   LeeSooHa                 NaT 2015-09-24 18:12:33
    1283         eng                         The password is "Muiriel".     wuiwie                 NaT 2019-03-24 11:45:36
    ...          ...                                                ...        ...                 ...                 ...
    9393217      eng  First, we stuff ham and cheese into the chicke...  DJ_Saidez 2020-11-28 05:53:59 2020-11-28 05:53:59
    9393221      eng               I've never seen a yellow cow before.  DJ_Saidez 2020-11-28 05:56:18 2020-11-28 05:56:18
    9393223      eng                Why are the eggs and the ham green?  DJ_Saidez 2020-11-28 05:56:37 2020-11-28 05:56:37
    9393229      eng                     My grandma made oatmeal atole.  DJ_Saidez 2020-11-28 05:58:31 2020-11-28 05:59:29
    9393234      eng                     How did these eggs get broken?         CK 2020-11-28 06:00:47 2020-11-28 06:00:47

    [1395738 rows x 5 columns]

    
Get the dataframe of all links for which French is the source language:

.. code-block:: python

    >>> tatoeba.get("links", ["fra", "*"])
    
             sentence_id  translation_id
    0               1115          136883
    1               1115          276353
    2               1115          334301
    3               1115          367406
    4               1115          472589
    ...              ...             ...
    1400415      9392546          267503
    1400416      9392546          540479
    1400417      9392546          565951
    1400418      9392546         2635684
    1400419      9392983         9232041

    [1400420 rows x 2 columns]
