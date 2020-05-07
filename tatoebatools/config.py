from pathlib import Path

from pkg_resources import resource_filename

DATA_DIR = Path(resource_filename(__package__, "data"))
