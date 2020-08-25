import logging

import requests
from bs4 import BeautifulSoup

from .config import INDEX_SPLIT_TABLES, SIMPLE_SPLIT_TABLES, SUPPORTED_TABLES
from .download import Download
from .exceptions import NotAvailableLanguage, NotAvailableTable
from .jpn_indices import JpnIndices
from .links import Links
from .sentences_base import SentencesBase
from .sentences_cc0 import SentencesCC0
from .sentences_detailed import SentencesDetailed
from .sentences_in_lists import SentencesInLists
from .sentences_with_audio import SentencesWithAudio
from .table import Table
from .tags import Tags
from .transcriptions import Transcriptions
from .update import check_updates
from .user_languages import UserLanguages
from .user_lists import UserLists
from .utils import lazy_property

logger = logging.getLogger(__name__)


class Tatoeba:
    """A handler for interacting with the local Tatoeba's data

    It enables users to update and parse their tables' data files.
    """

    def update(self, table_names, language_codes, verbose=True):
        """Updates the tables' datafiles and classify them by language

        Parameters
        ----------
        table_names : list
            The names of the tables to update. Call the 'all_tables' 
            attribute to get a list of all available tables
        language_codes : list
            ISO 639-3 codes of the languages for which local data is 
            updated. Call the 'all_languages' attribute to get the list 
            of all supported languages.
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
            table_names, language_codes, verbose=verbose
        )
        if verbose:
            logger.info(f"{len(to_download)} files to download")

        # download the files of the update
        updated_tables = {
            Download(url, vs).fetch() for url, vs in to_download.items()
        }

        # classify the multilingual datafiles by language
        language_index = {}
        for table_name in table_names:
            table = Table(table_name, language_codes)

            if (
                table_name in INDEX_SPLIT_TABLES
                and table_name in updated_tables
            ):
                if not language_index:
                    logger.info("mapping sentence ids to languages")

                    sentence_table = Table(
                        "sentences_detailed", language_codes
                    )
                    language_index = sentence_table.index(0, 1)

                table.classify(language_index)

            elif (
                table_name in updated_tables
                and table_name in SIMPLE_SPLIT_TABLES
            ):
                table.classify()

        if verbose:
            if updated_tables:
                msg = "{} updated".format(", ".join(updated_tables))
            else:
                msg = "data already up to date"

            logger.info(msg)

    def sentences_detailed(self, language):
        """Iterates through all sentences in this language.       

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages.

        Returns
        -------
        iterator
            SentenceDetailed instances with sentence_id, lang, 
            text, username, date_added and date_last_modified
            attributes.
        """

        return SentencesDetailed(language=language).__iter__()

    def sentences_base(self, language):
        """Iterates through all sentences' bases in this language.       

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages

        Returns
        -------
        iterator
            SentenceBase instances with sentence_id and 
            base_of_the_sentence attributes
        """

        return SentencesBase(language=language).__iter__()

    def sentences_CC0(self, language):
        """Iterate through all sentences in this language with a CC0 
        license

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages.        

        Returns
        -------
        iterator
            SentenceCC0 instances with sentence_id, lang, text and 
            date_last_modified attributes.
        """

        return SentencesCC0(language=language).__iter__()

    def links(self, source_language, target_language):
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

        Returns
        -------
        iterator
            Link instances with sentence_id and translation_id 
            attributes
        """

        return Links(
            source_language=source_language, target_language=target_language
        ).__iter__()

    def tags(self, language):
        """Iterates through all tagged sentences in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages.        

        Returns
        -------
        iterator
            Tag instances with sentence_id and tag_name attributes
        """

        return Tags(language=language).__iter__()

    def user_lists(self):
        """Iterate trough all sentences' lists

        Returns
        -------
        iterator
            UserList instances with list_id, username, date_created,
            date_last_modified, list_name and editable_by attributes
        """

        return UserLists().__iter__()

    def sentences_in_lists(self, language):
        """Iterates through all sentences in this language which 
        are in a list

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages.        

        Returns
        -------
        iterator
            SentenceInList instances with list_id and sentence_id
            attributes
        """

        return SentencesInLists(language=language).__iter__()

    def jpn_indices(self):
        """Iterates through all Japanese indices.

        Returns
        -------
        iterator
            JpnIndex instances with sentence_id, meaning_id and text
            attributes
        """

        return JpnIndices().__iter__()

    def sentences_with_audio(self, language):
        """Iterates through sentences with audio file.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages.        

        Returns
        -------
        iterator
            SentenceWithAudio instances with sentence_id, username,
            license and attribution_url attributes
        """

        return SentencesWithAudio(language=language).__iter__()

    def user_languages(self, language):
        """Iterates through all users' skills in this language.

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages.        

        Returns
        -------
        iterator
            UserLanguage instances with lang, skill_level, 
            username and details attributes
        """

        return UserLanguages(language=language).__iter__()

    def transcriptions(self, language):
        """Iterate through all transcriptions for this language

        Parameters
        ----------
        language : str
            The IS0 639-3 code of a Tatoeba supported language.
            Call the 'all_languages' attribute to get the list 
            of all supported languages.        

        Returns
        -------
        iterator
            Transcription instances with sentence_id, lang, 
            script_name, username and transcription attributes
        """

        return Transcriptions(language=language).__iter__()

    @property
    def all_tables(self):
        """All tables that are downloadable from tatoeba.org

        Returns
        -------
        list
            See https://tatoeba.org/eng/downloads for more information.
        """

        return sorted(list(SUPPORTED_TABLES))

    @lazy_property
    def all_languages(self):
        """All languages with at least one sentence on tatoeba.org

        Returns
        -------
        list
            See https://tatoeba.org/eng/stats/sentences_by_language
            for more information.
        """

        url = "https://downloads.tatoeba.org/exports/per_language/"
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            return []
        else:
            soup = BeautifulSoup(r.text, features="html.parser")
            links = [a.get("href") for a in soup.find_all("a")]

            return [lk[:-1] for lk in links if lk[:-1].isalpha()]
