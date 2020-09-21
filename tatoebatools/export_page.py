import logging
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from .config import DATA_DIR

logger = logging.getLogger(__name__)


class ExportPage:
    """A web page downloaded from tatoeba.org from
    which export files' versions can be scraped
    """

    dir = DATA_DIR.joinpath("export_pages")
    dir.mkdir(parents=True, exist_ok=True)

    def __init__(self, url):
        """
        url : str
            the url from which the web page is downloaded
        """
        self.url = url if url.endswith("/") else f"{url}/"
        self.path = self.dir.joinpath(self.name)

    def update(self, update_time=5):
        """Update the local web page

        Parameters
        ----------
        update_time : int, optional
            the time in minutes after which the local file of the web page 
            is re-downloaded, by default 5
        """
        if not self.version or self.version < datetime.now() - timedelta(
            minutes=update_time
        ):
            try:
                r = requests.get(self.url)
                with open(self.path, "w") as f:
                    f.write(r.text)
            except requests.exceptions.RequestException:
                logger.warning(f"error while requesting {self.url}")

    def get_versions(self):
        """Scrap the versions of the files listed in the web page

        Returns
        -------
        dict
            the versions of all urls listed in the web page
        """
        html = self._load()
        if html:
            versions = _extract_versions(html)
            return {f"{self.url}/{k}": v for k, v in versions.items()}
        else:
            return None

    def get_names(self):
        """Scraps the directory names listed in the web page

        Returns
        -------
        dict
            the names of all urls listed in the web page
        """
        html = self._load()
        if html:
            return _extract_names(html)
        else:
            return None

    def _load(self):
        """Loads the content of the local web page

        Returns
        -------
        str
            the HTML code of the page (if this one exists)
        """
        try:
            with open(self.path) as f:
                html = f.read()
        except FileNotFoundError:
            html = ""
        finally:
            return html

    @property
    def version(self):
        """Get the version of the local web page

        Returns
        -------
        datetime
            the last modification time of the file if this one exists
        """
        if self.path.is_file():
            return datetime.fromtimestamp(self.path.stat().st_mtime)
        else:
            return

    @property
    def name(self):
        """Get the name of the web page

        Returns
        -------
        str
            the name of the local web page file
        """
        stem = self.url[:-1].rsplit("/", 1)[-1]

        return f"{stem}.html"


def _extract_versions(html):
    """Extracts the versions of the files from an export page HTML code"""
    soup = BeautifulSoup(html, features="html.parser").find("pre")
    texts = [x.strip() for x in soup.findAll(text=True)]

    return {
        x: datetime.strptime(texts[i + 1][:17], "%d-%b-%Y %H:%M")
        for i, x in enumerate(texts)
        if i % 2 == 0 and texts[i + 1] and x[-1] != "/"
    }


def _extract_names(html):
    """Extracts the names of the directories from an export page HTML code"""
    soup = BeautifulSoup(html, features="html.parser")
    links = [a.get("href") for a in soup.find_all("a")]

    return [lk[:-1] for lk in links if lk[:-1].isalpha()]
