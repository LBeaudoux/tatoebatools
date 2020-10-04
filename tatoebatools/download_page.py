import logging
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from .config import DATA_DIR

logger = logging.getLogger(__name__)


class DownloadPages:
    """Web pages at downloads.tatoeba.org from
    which export files' versions can be scraped
    """

    dir = DATA_DIR.joinpath("export_pages")
    dir.mkdir(parents=True, exist_ok=True)

    def get_versions(self, url):
        """Scraps the versions of the files listed in the web page

        Returns
        -------
        dict
            the versions of all urls listed in the web page
        """
        html = self._get_html(url)
        versions = _extract_versions(html)

        return {self.url + k: v for k, v in versions.items()}

    def get_names(self, url):
        """Scraps the directory names listed in the web page

        Returns
        -------
        list
            the names of all urls listed in the web page
        """
        html = self._get_html(url)

        return _extract_names(html)

    def _get_html(self, url, update_time=5):
        """Get the HTML content of this web page

        Parameters
        ----------
        update_time : int, optional
            the time in minutes after which the local file of the web page
            is re-downloaded, by default 5
        """
        self.url = url if url.endswith("/") else f"{url}/"

        if not self.version or self.version < datetime.now() - timedelta(
            minutes=update_time
        ):
            # download a newer version
            try:
                r = requests.get(self.url)
                with open(self.path, "w") as f:
                    f.write(r.text)
            except requests.exceptions.RequestException:
                logger.warning(f"error while requesting {self.url}")
                return ""
            else:
                return r.text
        else:
            # load up to date local file
            with open(self.path) as f:
                return f.read()

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
    def path(self):
        """Get the local path of the web page

        Returns
        -------
        Path
            the local path of the file
        """
        stem = self.url[:-1].rsplit("/", 1)[-1]

        return self.dir.joinpath(f"{stem}.html")


def _extract_versions(html):
    """Extracts the versions of the files from an export page HTML code"""
    soup = BeautifulSoup(html, features="html.parser").find("pre")
    texts = [x.strip() for x in soup.findAll(text=True) if soup]

    return {
        x: datetime.strptime(texts[i + 1][:17], "%d-%b-%Y %H:%M")
        for i, x in enumerate(texts)
        if i % 2 == 0 and texts[i + 1] and x[-1] != "/"
    }


def _extract_names(html):
    """Extracts the names of the directories from an export page HTML code"""
    soup = BeautifulSoup(html, features="html.parser")
    links = [a.get("href") for a in soup.find_all("a") if soup]

    return [lk[:-1] for lk in links if lk[:-1].isalpha()]
