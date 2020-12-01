class NotTable(Exception):
    """Raised when a table name passed as argument is not valid"""

    def __init__(self, not_available_table):

        msg = f"'{not_available_table}' is not a valid table name"
        super().__init__(msg)

        self.table_names = not_available_table


class NotLanguagePair(Exception):
    """Raised when languages passed as language pair are not valid"""

    def __init__(self, lang_codes):

        super().__init__(f"{lang_codes} is not a valid language pair")

        self.language_codes = lang_codes


class NotLanguage(Exception):
    """Raised when the language passed is not valid"""

    def __init__(self, lang_codes):

        super().__init__(f"{lang_codes} is not a valid language")

        self.language_codes = lang_codes
