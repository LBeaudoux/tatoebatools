import logging

import requests
from bs4 import BeautifulSoup

from .config import INDEX_SPLIT_TABLES, SIMPLE_SPLIT_TABLES, SUPPORTED_TABLES
from .download import Download
from .exceptions import (
    NotAvailableLanguage,
    NotAvailableTable,
)
from .index import Index
from .jpn_indices import JpnIndices
from .links import Links
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
    """A handler for managing Tatoeba data on the client side.
    """

    def sentences_detailed(self, language):
        """Iterate through all sentences in this language.
        """
        return SentencesDetailed(language=language).__iter__()

    def sentences_CC0(self, language):
        """Iterate through all sentences in this language with a CC0 license.
        """
        return SentencesCC0(language=language).__iter__()

    def links(self, source_language, target_language):
        """Iterate through all links from sentences in this source language 
        to sentences in this target language
        """
        return Links(
            source_language=source_language, target_language=target_language
        ).__iter__()

    def tags(self, language):
        """Iterate through all taged sentences in this language.
        """
        return Tags(language=language).__iter__()

    def user_lists(self):
        """Iterate trough all sentences' lists.
        """
        return UserLists().__iter__()

    def sentences_in_lists(self, language):
        """Iterate through all sentences in this language which are in a list.
        """
        return SentencesInLists(language=language).__iter__()

    def jpn_indices(self):
        """Iterate through all Japanese indices.
        """
        return JpnIndices().__iter__()

    def sentences_with_audio(self, language):
        """Iterate through sentences with audio file.
        """
        return SentencesWithAudio(language=language).__iter__()

    def user_languages(self, language):
        """Iterate through all users' skills in this language.
        """
        return UserLanguages(language=language).__iter__()

    def transcriptions(self, language):
        """Iterate through all transcriptions for this language.
        """
        return Transcriptions(language=language).__iter__()

    def update(self, table_names, language_codes):
        """Update the tables and classify them by required language.
        """
        try:
            # check if the tables are available
            not_available_tables = set(table_names) - set(self.all_tables)
            if not_available_tables:
                raise NotAvailableTable(not_available_tables)

            # check if the language codes are available
            not_available_langs = set(language_codes) - set(self.all_languages)
            if not_available_langs:
                raise NotAvailableLanguage(not_available_langs)

            # sentences table can be added because it is necessary in case of
            # index splitting of files
            if (
                any(tn in INDEX_SPLIT_TABLES for tn in table_names)
                and "sentences_detailed" not in table_names
            ):
                table_names.append("sentences_detailed")

            # get the urls of the datafiles that need an update
            to_download = check_updates(table_names, language_codes)
            logger.info(f"{len(to_download)} files to download")

            # download the files of the update
            updated_tables = {
                Download(url, vs).fetch() for url, vs in to_download.items()
            }

            # classify the multilingual datafiles by language
            language_index = {}
            for tbl_name in table_names:
                tbl = Table(tbl_name, language_codes)

                if tbl_name in INDEX_SPLIT_TABLES and (
                    tbl_name in updated_tables
                    or "sentences_detailed" in updated_tables
                ):
                    if not language_index:
                        logger.info("mapping sentence ids to languages")
                        language_index = get_language_index(*language_codes)

                    tbl.classify(language_index)

                elif (
                    tbl_name in updated_tables
                    and tbl_name in SIMPLE_SPLIT_TABLES
                ):
                    tbl.classify()

        except (NotAvailableLanguage, NotAvailableLanguage) as e:
            logger.exception(e)
        else:
            if updated_tables:
                msg = "{} updated".format(", ".join(updated_tables))
            else:
                msg = "data already up to date"
            
            logger.info(msg)

            return updated_tables            

    @lazy_property
    def language_index(self):
        """Get the index that maps the sentences' ids to their language.
        """
        logger.info("mapping sentence ids to languages")

        return get_language_index(*self._lgs)

    @property
    def all_tables(self):
        """List all tables that are downloadable from tatoeba.org.
        """
        return sorted(list(SUPPORTED_TABLES))

    @lazy_property
    def all_languages(self):
        """List all languages available on tatoeba.org
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


def get_language_index(*languages):
    """Get the mapping between the sentences' ids and their language.
    """
    sentence_tbl = Table("sentences_detailed", languages)

    return {
        id: lg
        for df in sentence_tbl.language_detafiles
        for id, lg in Index(df, 0, 1)
    }
