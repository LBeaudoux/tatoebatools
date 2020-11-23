from .utils import is_na


class UserLanguage:
    """The self-reported skill level of a user in a language"""

    def __init__(self, lang, skill_level, username, details):
        # the language
        self._lg = lang
        # the leval of the user in this language
        self._skl = skill_level
        # the name of the user
        self._usr = username
        # optional comments
        self._dtl = details

    @property
    def lang(self):
        """Get the language for this user skill"""
        return self._lg

    @property
    def skill_level(self):
        """Get the value of this skill level"""
        return int(self._skl) if not is_na(self._skl) else None

    @property
    def username(self):
        """Get the name of the user who have this language skill"""
        return self._usr if not is_na(self._usr) else None

    @property
    def details(self):
        """Get more details about this user's language skill."""
        return self._dtl
