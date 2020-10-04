import logging

from .config import DIFFERENCE_TABLES, INDEX_SPLIT_TABLES, SIMPLE_SPLIT_TABLES
from .datafile import DataFile
from .download import Download
from .exceptions import NotAvailableLanguage, NotAvailableTable
from .jpn_indices import JpnIndices
from .links import Links
from .queries import Queries
from .sentences_base import SentencesBase
from .sentences_cc0 import SentencesCC0
from .sentences_detailed import SentencesDetailed
from .sentences_in_lists import SentencesInLists
from .sentences_with_audio import SentencesWithAudio
from .table import Table
from .tags import Tags
from .transcriptions import Transcriptions
from .update import check_languages, check_tables, check_updates
from .user_languages import UserLanguages
from .user_lists import UserLists
from .utils import lazy_property

logger = logging.getLogger(__name__)


class Tatoeba:
    """A handler for interacting with the local Tatoeba's data
    It enables users to download and parse Tatoeba export files
    """

    def sentences_detailed(
        self, language, scope="all", update=True, verbose=False
    ):
        """Iterates through all sentences in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            SentenceDetailed instances with sentence_id, lang,
            text, username, date_added and date_last_modified
            attributes.
        """
        if update:
            self.update(["sentences_detailed"], [language], verbose=verbose)

        return SentencesDetailed(language=language, scope=scope).__iter__()

    def sentences_base(
        self, language, scope="all", update=True, verbose=False
    ):
        """Iterates through all sentences' bases in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            SentenceBase instances with sentence_id and
            base_of_the_sentence attributes
        """
        if update:
            self.update(["sentences_base"], [language], verbose=verbose)

        return SentencesBase(language=language).__iter__()

    def sentences_CC0(self, language, scope="all", update=True, verbose=False):
        """Iterate through all sentences in this language with a CC0
        license

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            SentenceCC0 instances with sentence_id, lang, text and
            date_last_modified attributes.
        """
        if update:
            self.update(["sentences_CC0"], [language], verbose=verbose)

        return SentencesCC0(language=language).__iter__()

    def links(
        self,
        source_language,
        target_language,
        scope="all",
        update=True,
        verbose=False,
    ):
        """Iterates through all links between sentences in this source
        language and sentences in this target language

        Parameters
        ----------
        source_language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        target_language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            Link instances with sentence_id and translation_id
            attributes
        """
        if update:
            self.update(
                ["links"],
                [source_language, target_language],
                oriented_pair=True,
                verbose=verbose,
            )

        return Links(
            source_language=source_language, target_language=target_language
        ).__iter__()

    def tags(self, language, scope="all", update=True, verbose=False):
        """Iterates through all tagged sentences in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            Tag instances with sentence_id and tag_name attributes
        """
        if update:
            self.update(["tags"], [language], verbose=verbose)

        return Tags(language=language).__iter__()

    def user_lists(self, scope="all", update=True, verbose=False):
        """Iterate trough all sentences' lists

        Parameters
        ----------
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            UserList instances with list_id, username, date_created,
            date_last_modified, list_name and editable_by attributes
        """
        if update:
            self.update(["user_lists"], [], verbose=verbose)

        return UserLists().__iter__()

    def sentences_in_lists(
        self, language, scope="all", update=True, verbose=False
    ):
        """Iterates through all sentences in this language which
        are in a list

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages.
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            SentenceInList instances with list_id and sentence_id
            attributes
        """
        if update:
            self.update(["sentences_in_lists"], [language], verbose=verbose)

        return SentencesInLists(language=language).__iter__()

    def jpn_indices(self, scope="all", update=True, verbose=False):
        """Iterates through all Japanese indices

        Parameters
        ----------
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            JpnIndex instances with sentence_id, meaning_id and text
            attributes
        """
        if update:
            self.update(["jpn_indices"], [], verbose=verbose)

        return JpnIndices().__iter__()

    def sentences_with_audio(
        self, language, scope="all", update=True, verbose=False
    ):
        """Iterates through sentences with audio file

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            SentenceWithAudio instances with sentence_id, username,
            license and attribution_url attributes
        """
        if update:
            self.update(["sentences_with_audio"], [language], verbose=verbose)

        return SentencesWithAudio(language=language).__iter__()

    def user_languages(
        self, language, scope="all", update=True, verbose=False
    ):
        """Iterates through all users' skills in this language

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            UserLanguage instances with lang, skill_level,
            username and details attributes
        """
        if update:
            self.update(["user_languages"], [language], verbose=verbose)

        return UserLanguages(language=language).__iter__()

    def transcriptions(
        self, language, scope="all", update=True, verbose=False
    ):
        """Iterate through all transcriptions for this language

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            Transcription instances with sentence_id, lang,
            script_name, username and transcription attributes
        """
        if update:
            self.update(["transcriptions"], [language], verbose=verbose)

        return Transcriptions(language=language).__iter__()

    def queries(self, language, scope="all", update=True, verbose=False):
        """Iterate through all queries for this language

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list
            of all supported languages
        scope : str
            The scope of the iteration is "all", "added" or "removed"
        update : bool
            The data file is updated before being read when update is
            activated
        verbose : bool
            Update steps are printed when verbose is set to True

        Returns
        -------
        iterator
            Queries instances with date, language and content
            attributes
        """
        if update:
            self.update(["queries"], [language], verbose=verbose)

        return Queries(language=language, scope=scope).__iter__()

    def update(
        self, table_names, language_codes, oriented_pair=False, verbose=False
    ):
        """Updates the local Tatoeba datafiles:
        - download newest versions of the datafiles
        - split them by language (when nomonolingual versions not avialable)
        - identify the differences with the previously downloaded versions

        Parameters
        ----------
        table_names : list
            The names of the tables to update. Call the 'all_tables'
            attribute to get a list of all available tables
        language_codes : list
            ISO 639-3 codes of the languages for which local data is
            updated. Call the 'all_languages' attribute to get the list
            of all supported languages.
        oriented_pair : bool, optional
            Requires a pair of language codes where the first language
            is considered as source and the second as target,
            by default False
        verbose : bool, optional
            Verbosity of the logging, by default True

        Raises
        ------
        NotAvailableTable
            Indicates that at least one of the table naames pased as
            argument is not a valid Tatoeba table name.
        NotAvailableLanguage
            Indicates that at least one of the language code pased as
            argument is not supported by Tatoeba.
        """
        if not table_names and not language_codes:
            return

        # check if the tables are available
        not_available_tables = set(table_names) - set(self.all_tables)
        if not_available_tables:
            raise NotAvailableTable(not_available_tables)

        # check if the language codes are available
        not_available_langs = set(language_codes) - set(self.all_languages)
        if not_available_langs:
            raise NotAvailableLanguage(not_available_langs)

        # sentences table added when required for splitting other files
        if (
            any(tn in INDEX_SPLIT_TABLES for tn in table_names)
            and "sentences_detailed" not in table_names
        ):
            table_names.append("sentences_detailed")

        # get the urls of the datafiles that need an update
        to_download = check_updates(
            table_names,
            language_codes,
            oriented_pair=oriented_pair,
            verbose=verbose,
        )

        # download the files of the update
        download_paths = []
        for url, vs in to_download.items():
            download_paths.extend(Download(url, vs).fetch())

        language_index = {}
        monolang_datafiles = []
        for fp in download_paths:
            # split the multilingual datafiles by language
            if fp.stem in table_names:
                table = Table(fp.stem, language_codes)

                if table.name in INDEX_SPLIT_TABLES:
                    if not language_index:
                        logger.info("mapping sentence ids to languages")

                        sentence_table = Table(
                            "sentences_detailed", language_codes
                        )
                        language_index = sentence_table.index(0, 1)

                    monolang_datafiles.extend(table.classify(language_index))

                elif table.name in SIMPLE_SPLIT_TABLES:
                    monolang_datafiles.extend(table.classify())

            else:
                delimiter = "\t" if fp.suffix == ".tsv" else ","
                monolang_datafiles.append(DataFile(fp, delimiter=delimiter))

        # compare monolingual datafiles with their older version
        for df in monolang_datafiles:
            if any(tbl in df.stem for tbl in DIFFERENCE_TABLES):
                df.find_changes(index_col_keys=None)

        if verbose:
            updated = {fp.stem for fp in download_paths}
            updated |= {df.stem for df in monolang_datafiles}
            updated = sorted(list(updated))
            if updated:
                msg = "updated files: {}".format(", ".join(updated))
                logger.info(msg)

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
