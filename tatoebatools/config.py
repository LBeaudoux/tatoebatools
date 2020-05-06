from pathlib import Path

from pkg_resources import resource_filename

LINKS_DIR = Path(resource_filename(__package__, "data/links/"))
SENTENCES_DIR = Path(resource_filename(__package__, "data/sentences_detailed"))
