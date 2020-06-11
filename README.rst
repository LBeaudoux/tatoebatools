tatoebatools is a Python library for easily downloading and iterating over data from the Tatoeba project.


Installation
------------

This library requires Python 3.6. 

.. code:: sh

    pip3 install tatoebatools


Basic usage
-----------

Thanks to the Corpus top-level object, you can download all sentences in a language and iterate over them:

.. code-block:: python

    >>> from tatoebatools import Corpus

    >>> corpus = Corpus("fra")
    >>> for s in corpus:
            print(s.sentence_id, s.text, s.username)
    ...
    7875 Laissez-moi vous aider. TRANG
    7876 Donne-m'en quelques-uns. sacredceltic
    7877 Pouvez-vous me consacrer un peu de temps ? Cocorico
    7878 S'il te plaît, donne-moi de l'eau. gillux
    7879 C'est elle qui me l'a dit. Archibald
    ...


Thanks to the ParallelCorpus top-level object, you can download all sentence/translation pairs from a source language to a target language and iterate over them:

.. code-block:: python

    >>> from tatoebatools import ParallelCorpus

    >>> parallel_corpus = ParallelCorpus("cmn", "eng")
    >>> for sentence, translation in parallel_corpus:
            print(sentence.text, translation.text)
    ...
    我不知道这个词的意思。 I don't know the meaning of this word.
    昨晚雨下得很大。 It rained hard last night.
    我们都非常喜欢你。 All of us like you very much.
    我是素食主义者。 I am a vegetarian.
    我最喜歡吃葡萄果凍。 I like grape jelly best.
    ...
