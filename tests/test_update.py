from tatoebatools.update import _scrap_versions, requests
from unittest.mock import patch
from datetime import datetime


url = "https://downloads.tatoeba.org/exports/per_language/eng"

html = (
    "<html>\r\n"
    "<head><title>Index of /exports/per_language/eng/</title></head>\r\n"
    '<body bgcolor="white">\r\n'
    "<h1>Index of /exports/per_language/eng/</h1>"
    "<hr><pre>"
    '<a href="../">../</a>\r\n'
    '<a href="eng_sentences.tsv.bz2">'
    "eng_sentences.tsv.bz2</a>"
    "                              23-May-2020 06:25            14828881\r\n"
    '<a href="eng_sentences_CC0.tsv.bz2">'
    "eng_sentences_CC0.tsv.bz2</a>"
    "                          23-May-2020 06:25               96899\r\n"
    '<a href="eng_sentences_detailed.tsv.bz2">'
    "eng_sentences_detailed.tsv.bz2</a>"
    "                     23-May-2020 06:23            19841380\r\n"
    "</pre><hr>"
    "</body>\r\n"
    "</html>\r\n"
)

ok_versions = {
    f"{url}/eng_sentences.tsv.bz2": datetime(2020, 5, 23, 6, 25),
    f"{url}/eng_sentences_CC0.tsv.bz2": datetime(2020, 5, 23, 6, 25),
    f"{url}/eng_sentences_detailed.tsv.bz2": datetime(2020, 5, 23, 6, 23),
}


@patch.object(requests, "get")
def test_scrap_versions(m_get):
    m_get.return_value.text = html
    versions = _scrap_versions(url)
    m_get.assert_called_once_with(url)
    assert versions == ok_versions
