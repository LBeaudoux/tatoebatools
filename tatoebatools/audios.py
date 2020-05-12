import csv
import logging

from .config import DATA_DIR
from .utils import lazy_property
from .version import Version


class Audios:
    """The Tatoeba sentences with audio for a given language.
    """

    _dir = DATA_DIR.joinpath("sentences_with_audio")

    def __init__(self, language):

        self._lg = language

    def __iter__(self):

        try:
            with open(self.path) as f:
                fieldnames = [
                    "sentence_id",
                    "username",
                    "license",
                    "attribution_url",
                ]
                rows = csv.DictReader(f, delimiter="\t", fieldnames=fieldnames)
                for row in rows:
                    yield Audio(**row)
        except OSError:
            logging.exception(f"an error occurred while reading {self.path}")

    @property
    def language(self):
        """Get the language of these sentences with audio.
        """
        return self._lg

    @property
    def path(self):
        """Get the path where the sentences with audio are saved.
        """
        return Audios._dir.joinpath(self.filename)

    @property
    def filename(self):
        """Get the name of the file where the sentences with audio are saved.
        """
        return f"{self._lg}_sentences_with_audio.csv"

    @lazy_property
    def sentence_ids(self):
        """Get the ids of the sentences with audio.
        """
        return {audio.sentence_id for audio in self}

    @lazy_property
    def version(self):
        """Get the version of these sentences with audio.
        """
        with Version() as vs:
            return vs[self.filename]


class Audio:
    """A Tatoeba sentence with audio.
    """

    def __init__(self, sentence_id, username, license, attribution_url):

        self._id = sentence_id
        self._usr = username
        self._lic = license
        self._atr = attribution_url

    @property
    def sentence_id(self):
        """The id of the sentence with audio.
        """
        return int(self._src_id)

    @property
    def username(self):
        """The username that added the sentence with audio.
        """
        return self._usr

    @property
    def license(self):
        """The license of the sentence with audio.
        """
        return self._lic

    @property
    def attribution_url(self):
        """The url to the attrbution of the sentence with audio.
        """
        return self._atr
