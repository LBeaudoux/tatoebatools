import logging
from pathlib import Path

from .config import DATA_DIR
from .table import Table
from .update import check_languages, check_tables
from .utils import lazy_property
from .version import version

logger = logging.getLogger(__name__)


class Tatoeba:
    """A handler for interacting with Tatoeba data

    Use it to download and parse Tatoeba export data files.

    Find out more about Tatoeba export data files at:
    https://tatoeba.org/eng/downloads
    """

    def __init__(self, data_dir=None):
        """
        Parameters
        ----------
        data_dir : str, optional
            The path of the directory where the Tatoeba data is saved
            If None, the data is saved into the tatoebatools package
        """
        self._dir = Path(data_dir) if data_dir else DATA_DIR
        if version.dir != self._dir:
            version.dir = self._dir

    def sentences_detailed(
        self, language, scope="all", update=True, verbose=True
    ):
        """Iterates through all sentences in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            SentenceDetailed instances with sentence_id, lang,
            text, username, date_added and date_last_modified
            attributes.
        """
        return iter(
            Table(
                "sentences_detailed",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def sentences_base(self, language, scope="all", update=True, verbose=True):
        """Iterates through all sentences' bases in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            SentenceBase instances with sentence_id and
            base_of_the_sentence attributes
        """
        return iter(
            Table(
                "sentences_base",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def sentences_CC0(self, language, scope="all", update=True, verbose=True):
        """Iterate through all sentences in this language with a CC0
        license

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            SentenceCC0 instances with sentence_id, lang, text and
            date_last_modified attributes.
        """
        return iter(
            Table(
                "sentences_CC0",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def links(
        self,
        source_language,
        target_language,
        scope="all",
        update=True,
        verbose=True,
    ):
        """Iterates through all links between sentences in this source
        language and sentences in this target language

        Parameters
        ----------
        source_language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        target_language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            Link instances with sentence_id and translation_id
            attributes
        """
        return iter(
            Table(
                "links",
                language_codes=[source_language, target_language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def tags(self, language, scope="all", update=True, verbose=True):
        """Iterates through all tagged sentences in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            Tag instances with sentence_id and tag_name attributes
        """
        return iter(
            Table(
                "tags",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def user_lists(self, scope="all", update=True, verbose=True):
        """Iterate trough all sentences' lists

        Parameters
        ----------
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            UserList instances with list_id, username, date_created,
            date_last_modified, list_name and editable_by attributes
        """
        return iter(
            Table(
                "user_lists",
                language_codes=[],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def sentences_in_lists(
        self, language, scope="all", update=True, verbose=True
    ):
        """Iterates through all sentences in this language which
        are in a list

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            SentenceInList instances with list_id and sentence_id
            attributes
        """
        return iter(
            Table(
                "sentences_in_lists",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def jpn_indices(self, scope="all", update=True, verbose=True):
        """Iterates through all Japanese indices

        Parameters
        ----------
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            JpnIndex instances with sentence_id, meaning_id and text
            attributes
        """
        return iter(
            Table(
                "jpn_indices",
                language_codes=[],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def sentences_with_audio(
        self, language, scope="all", update=True, verbose=True
    ):
        """Iterates through sentences with audio file

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            SentenceWithAudio instances with sentence_id, username,
            license and attribution_url attributes
        """
        return iter(
            Table(
                "sentences_with_audio",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def user_languages(self, language, scope="all", update=True, verbose=True):
        """Iterates through all users' skills in this language

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            UserLanguage instances with lang, skill_level,
            username and details attributes
        """
        return iter(
            Table(
                "user_languages",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def transcriptions(self, language, scope="all", update=True, verbose=True):
        """Iterate through all transcriptions for this language

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            Transcription instances with sentence_id, lang,
            script_name, username and transcription attributes
        """
        return iter(
            Table(
                "transcriptions",
                language_codes=[language],
                data_dir=self._dir,
                scope=scope,
                update=update,
                verbose=verbose,
            )
        )

    def queries(self, language, update=True, verbose=True):
        """Iterate through all queries for this language

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Use '*' to designate all supported languages.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        update : bool
            Whether a data file is updated before being read, by default True
        verbose : bool
            Whether update steps are printed, by default True

        Returns
        -------
        iterator
            Queries instances with date, language and content
            attributes
        """
        return iter(
            Table(
                "queries",
                language_codes=[language],
                data_dir=self._dir,
                scope="all",
                update=update,
                verbose=verbose,
            )
        )

    def get(
        self,
        table_name,
        language_codes,
        scope="all",
        row_filters=[],
        update=True,
        verbose=True,
        **read_csv_parameters
    ):
        """Get the DataFrame of a monolinguel or multilingual Tatoeba table

        Parameters
        ----------
        table_name : str
            A Tatoeba table name (e.g. 'sentences_detailed' or 'links')
            Call the 'all_tables' attribute to get the list
            of all supported tables.
        language_codes : list
            The IS0 639-3 code of a Tatoeba supported language or '*' to
            designate all supported languages.
            With the 'links' table, a pair of language codes is required.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str, optional
            The scope of the data.
            Use default 'all' to get all latest data. Use 'added' or 'removed'
            to get only differences with the former local data.
        row_filters : list, optional
            Row filters can be passed to load only useful rows into memory.
            A row filter is a dict instance containing:
            'col_index': the column for which the rows are filtered by value
            'ok_values': the allowed values in the filter column
            'converter' (optional): a converter applied to the filter column
        update : bool, optional
            Whether a data file is updated before being read, by default True
        verbose : bool, optional
            Whether update steps are printed, by default True
        read_csv_parameters : dict, optional
            The tatoebatools default configuration can be overwritten by
            providing these parameters to 'pandas.read_csv'.
            See 'config.py' for more information about the default parameters.

        Returns
        -------
        pandas.DataFrame
            The dataframe object of a Tatoeba export datafile
        """
        table = Table(
            table_name,
            language_codes=language_codes,
            data_dir=self._dir,
            scope=scope,
            row_filters=row_filters,
            update=update,
            verbose=verbose,
        )

        return table.as_dataframe(**read_csv_parameters)

    @property
    def all_tables(self):
        """All tables that are downloadable from tatoeba.org

        Returns
        -------
        list
            See https://tatoeba.org/eng/downloads for more information.
        """
        return check_tables()

    @lazy_property
    def all_languages(self):
        """All languages with at least one sentence on tatoeba.org

        Returns
        -------
        list
            See https://tatoeba.org/eng/stats/sentences_by_language
            for more information.
        """
        return check_languages()

    @property
    def dir(self):
        """Gets the local directory where the Tatoeba data is saved"""
        return self._dir

    @dir.setter
    def dir(self, new_data_dir):
        """Sets the local directory where the Tatoeba data is saved"""
        if self._dir != Path(new_data_dir):
            self._dir = Path(new_data_dir) if new_data_dir else DATA_DIR
            version.dir = self._dir
