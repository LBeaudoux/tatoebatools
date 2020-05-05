from .config import LINKS_DIR, SENTENCES_DIR
from .corpus import Corpus
from .datafile import DataFile, LinksFile
from .version import Versions

versions = Versions()


def update(*language_codes):
    """Update all data files required for these languages.
    """
    dl_url = "https://downloads.tatoeba.org/exports"

    # update sentences' datafiles
    for lg in language_codes:
        filename = f"{lg}_sentences_detailed.tsv"
        endpoint = f"{dl_url}/per_language/{lg}"

        sentences_file = DataFile(filename, endpoint, SENTENCES_DIR)
        sentences_file.fetch()
        versions.update(sentences_file.name, sentences_file.online_version)

    # update links' datafiles
    links_file = LinksFile("links.csv", dl_url, LINKS_DIR, is_archived=True)
    links_file.fetch()
    versions.update(links_file.name, links_file.online_version)

    lang_mapping = {s.id: s.lang for lg in language_codes for s in Corpus(lg)}
    links_file.classify(lang_mapping)
