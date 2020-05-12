from .links import Links
from .tatoeba import Tatoeba
from .sentences import Sentences


# Tatoeba is imported so that other things can import
# them from here. Suppress the flake8 warning.
Tatoeba = Tatoeba
Sentences = Sentences
Links = Links


def update(tables, language_codes):
    """
    """
    tatoeba = Tatoeba(*language_codes)

    return tatoeba.update(*tables)


def update_all():
    """
    """
    tatoeba = Tatoeba()
    all_tables = tatoeba.downloadable_tables

    return tatoeba.update(*all_tables)
