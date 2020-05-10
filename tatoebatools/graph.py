import networkx as nx

from .links import Links
from .sentences import Sentences


class Graph:
    """
    """

    def __init__(self, *language_codes):

        # the languages of the sentences in the graph
        self._lgs = language_codes

        # initialize the directional graph instance
        self._g = nx.DiGraph()

        # Add sentences to the graph as nodes
        for lg in self._lgs:
            for st in Sentences(lg):
                self._add_sentence(st)

        # Add translations as edges to the graph
        for src_lg in self._lgs:
            for tgt_lg in self._lgs:
                for lk in Links(src_lg, tgt_lg):
                    self._add_translation(lk)

    def _add_sentence(self, sentence):
        """Add a sentence to the graph as a node identified by the sentence's 
        id and tagged by its language, username and date of addition.
        """
        tags = {
            "lang": sentence.lang,
            "user": sentence.username,
            "added": sentence.date_added,
        }
        self._g.add_node(sentence.id, **tags)

    def _add_translation(self, link):
        """Add the translation of a sentence as a new directed edge in the 
        graph if the target sentence was created after the source sentence.
        """
        if (
            link.translation_id > link.sentence_id
            and link.sentence_id in self._g
            and link.translation_id in self._g
        ):
            self._g.add_edge(link.sentence_id, link.translation_id)

    def get_direct_translations(self, sentence_id):
        """
        """
        return set(self._g.successors(sentence_id))

    def get_all_translations(self, sentence_id):
        """Get all the sentences translated directly or indirectly from this
        sentence.
        """
        all_translations = self.get_direct_translations(sentence_id)
        to_check = set(all_translations)
        checked = set()
        while to_check:
            id = to_check.pop()

            new_translations = self.get_direct_translations(id)
            all_translations |= new_translations

            checked.add(id)
            new_to_check = new_translations - checked
            to_check |= new_to_check

        return all_translations

    def get_target_languages(self, sentence_id):
        """
        """
        pass

    def get_degree(self, sentence_id):
        """
        """
        pass
