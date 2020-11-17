class NoDataFile(Exception):
    """Raised when the datafile read is not locally available"""

    def __init__(self, path_datafile_not_found):

        datafile_name = path_datafile_not_found.name
        parent_dir = path_datafile_not_found.parent
        msg = f"{datafile_name} not found at {parent_dir}"

        super().__init__(msg)

        self.path_datafile_not_found = path_datafile_not_found


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
    available
    """

    def __init__(self, not_available_langs):

        if "*" in not_available_langs:
            msg = "'*' cannot be passed in addition to language codes"
        else:
            s1 = len(not_available_langs)
            s2 = "s" if s1 > 1 else ""
            s3 = ", ".join(not_available_langs)
            msg = f"{s1} not available language{s2}: {s3}"

        super().__init__(msg)

        self.language_codes = not_available_langs


class NotLanguagePair(Exception):
    """Raised when languages passed as language pair are not valid"""

    def __init__(self, lang_codes):

        s = ", ".join(lang_codes)
        msg = f"['{s}'] is not a valid language pair"

        super().__init__(msg)

        self.language_codes = lang_codes


class NotLanguage(Exception):
    """Raised when the language passed is not valid"""

    def __init__(self, lang_codes):

        s = ", ".join(lang_codes)
        msg = f"['{s}'] is not a valid language"

        super().__init__(msg)

        self.language_codes = lang_codes
