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
    
    def __init__(self, *, title_match: str | None = _MISSING, description_match: str | None = _MISSING,
                 author_name: str | None = _MISSING, author_icon_url: str | None = _MISSING,
                 author_url: str | None = _MISSING):
        self._title_match = title_match
        self._description_match = description_match
        self._author_name = author_name
        self._author_icon_url = author_icon_url
        self._author_url = author_url
        
    def matches_fully(self, embed: discord.Embed):
        self._matches(embed, False)

    def matches_configured(self, embed: discord.Embed):
        self._matches(embed, True)

    def _matches(self, embed: discord.Embed, match_all_if_not_set: bool):
        values = [(_get_pattern(self._title_match, match_all_if_not_set), embed.title, "title"),
                  (_get_pattern(self._description_match, match_all_if_not_set), embed.description, "description")]
        if self._validate_author_existence(embed, match_all_if_not_set):
            values += [(_get_pattern(self._author_name, match_all_if_not_set), embed.author.name, "author.name"),
                       (_get_pattern(self._author_icon_url, match_all_if_not_set), embed.author.icon_url, 
                        "author.icon_url"),
                       (_get_pattern(self._author_url, match_all_if_not_set), embed.author.url, "author.url")]
        
        for pattern, field, field_name in values:
            assert _compare_value(pattern, field), f"Expected field '{field_name}' to match pattern '{pattern}', but " \
                                                   f"found '{field}' instead."
    
    def _validate_author_existence(self, embed: discord.Embed, match_all_if_not_set: bool) -> bool:
        if not embed.author:
            self._validate_none_author(match_all_if_not_set)
            return False
        return True

    def _validate_none_author(self, match_all_if_not_set):
        assert self._author_icon_url is _MISSING, "Expected to have author icon url data in embed but found no " \
                                                  "author data."
        assert self._author_url is _MISSING, "Expected to have author url data in embed but found no author data."
        assert self._author_name is _MISSING, "Expected to have author name data in embed but found no author data."
