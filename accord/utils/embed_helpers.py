import re

import discord

_MATCH_ALL = r".*"


class _NoneSentinel:
    pass


_MISSING = _NoneSentinel()


def _compare_value(pattern: str | None, field: str | None) -> bool:
    if pattern is None:
        return field is None
    if pattern != _MATCH_ALL and field is None:
        return False
    return bool(re.match(pattern, field))


def _get_pattern(field: str | None | _NoneSentinel, match_all_if_not_set: bool) -> str | None:
    if field is _MISSING and match_all_if_not_set:
        return _MATCH_ALL
    return None if field is _MISSING else field


class EmbedVerifier:
    
    def __init__(self, *, title_match: str | None = _MISSING, description_match: str | None = _MISSING):
        self._title_match = title_match
        self._description_match = description_match
        
    def matches_fully(self, embed: discord.Embed):
        self._matches(embed, False)

    def _matches(self, embed, match_all_if_not_set):
        values = ((_get_pattern(self._title_match, match_all_if_not_set), embed.title, "title"),
                  (_get_pattern(self._description_match, match_all_if_not_set), embed.description, "description"))
        for pattern, field, field_name in values:
            assert _compare_value(pattern, field), f"Expected field '{field_name}' to match pattern '{pattern}', but " \
                                                   f"found '{field}' instead."

    def matches_configured(self, embed: discord.Embed):
        self._matches(embed, True)
                
