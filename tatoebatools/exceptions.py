class NoDataFile(Exception):
    """Raised when the datafile read is not locally available"""


class NotAvailableTable(Exception):
    """Raised when a table passed as argument to the update is not
    available"""

    def __init__(self, not_available_tables):

        s1 = len(not_available_tables)
        s2 = "s" if s1 > 1 else ""
        s3 = ", ".join(not_available_tables)
        msg = f"{s1} not available table{s2}: {s3}"

        super().__init__(msg)

        self.table_names = not_available_tables


class NotAvailableLanguage(Exception):
    """Raised when a language passed as argument to the update is not
    available"""

    def __init__(self, not_available_langs):

        s1 = len(not_available_langs)
        s2 = "s" if s1 > 1 else ""
        s3 = ", ".join(not_available_langs)
        msg = f"{s1} not available language{s2}: {s3}"

        super().__init__(msg)

        self.language_codes = not_available_langs


class NotLanguagePair(Exception):
    """Raised when oriented_pair is activated and the number of
    languages passed as argument to the update differs from two
    """

    def __init__(self, lang_codes):

        s = ", ".join(lang_codes)
        msg = f"activated 'oriented_pair' requires [{s}] to be a language pair"

        super().__init__(msg)

        self.language_codes = lang_codes
