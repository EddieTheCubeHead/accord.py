import re
import typing

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


EmbedField = tuple[str | None, str | None, bool] | tuple[str | None, str | None]


def _find_embed_field(expected_field: EmbedField, fields: list[typing.Any],
                      searched_indexes: list[int], match_all_if_not_set: bool) -> int:
    for index, field in enumerate(fields):
        if index in searched_indexes:
            continue
        if len(expected_field) >= 3 and expected_field[2] != field.inline:
            continue
        if not _compare_value(_get_pattern(expected_field[0], match_all_if_not_set), field.name):
            continue
        if _compare_value(_get_pattern(expected_field[1], match_all_if_not_set), field.value):
            return index
    inline_notification = "" if len(expected_field) < 3 else f" with inline set to {expected_field[2]}"
    raise AssertionError(f"Expected to find field with name '{expected_field[0]}' and value '{expected_field[1]}'"
                         f"{inline_notification} in the embed fields. Fields {searched_indexes} were ignored "
                         f"because they were used in earlier verifications.")


class EmbedVerifier:
    
    def __init__(self, *, title_match: str | None = _MISSING, description_match: str | None = _MISSING,
                 author_name: str | None = _MISSING, author_icon_url: str | None = _MISSING,
                 author_url: str | None = _MISSING, fields: list[EmbedField] | None = _MISSING,
                 colour: int | None = _MISSING):
        self._title_match = title_match
        self._description_match = description_match
        self._author_name = author_name
        self._author_icon_url = author_icon_url
        self._author_url = author_url
        self._fields = fields
        self._colour = colour
        
    def matches_fully(self, embed: discord.Embed):
        self._matches(embed, False, False, False)

    def matches_configured(self, embed: discord.Embed, *, allow_extra_fields: bool = False, 
                           allow_any_field_order: bool = False):
        self._matches(embed, True, allow_extra_fields, allow_any_field_order)

    def _matches(self, embed: discord.Embed, match_all_if_not_set: bool, allow_extra_fields: bool, 
                 allow_any_field_order: bool):
        values = [(_get_pattern(self._title_match, match_all_if_not_set), embed.title, "title"),
                  (_get_pattern(self._description_match, match_all_if_not_set), embed.description, "description")]
        if self._validate_author_existence(embed):
            values += [(_get_pattern(self._author_name, match_all_if_not_set), embed.author.name, "author.name"),
                       (_get_pattern(self._author_icon_url, match_all_if_not_set), embed.author.icon_url, 
                        "author.icon_url"),
                       (_get_pattern(self._author_url, match_all_if_not_set), embed.author.url, "author.url")]
        for pattern, field, field_name in values:
            assert _compare_value(pattern, field), f"Expected field '{field_name}' to match pattern '{pattern}', but " \
                                                   f"found '{field}' instead."
        self._validate_fields(embed, match_all_if_not_set, allow_extra_fields, allow_any_field_order)
        self._validate_colour(embed, match_all_if_not_set)
    
    def _validate_author_existence(self, embed: discord.Embed) -> bool:
        if not embed.author:
            self._validate_none_author()
            return False
        return True

    def _validate_none_author(self):
        assert self._author_name is _MISSING, "Expected to have author name data in embed but found no author data."
        assert self._author_icon_url is _MISSING, "Expected to have author icon url data in embed but found no " \
                                                  "author data."
        assert self._author_url is _MISSING, "Expected to have author url data in embed but found no author data."
        
    def _validate_fields(self, embed: discord.Embed, match_all_if_not_set: bool,  allow_extra_fields: bool, 
                         allow_any_order: bool):
        if self._fields is _MISSING:
            self._fields = [] if allow_extra_fields else None
        
        if self._fields is None:
            assert len(embed.fields) == 0, f"Expected to find no fields in embed, but found {len(embed.fields)} fields."
            return
            
        if not allow_extra_fields:
            expected_string = f"{len(self._fields)} field{'s' if len(self._fields) > 1 else ''}"
            actual_string = f"{len(embed.fields)} field{'s' if len(embed.fields) > 1 else ''}"
            assert len(self._fields) == len(embed.fields), f"Expected to find {expected_string} in embed, " \
                                                           f"but found {actual_string} instead."

        searched_indexes = []
        for expected_index, expected_field in enumerate(self._fields):
            actual_index = _find_embed_field(expected_field, embed.fields, searched_indexes, match_all_if_not_set)
            searched_indexes.append(actual_index)
            if not allow_any_order:
                assert expected_index == actual_index,\
                    f"Expected to find field '{expected_field[0]}' in index {expected_index}, but was in index " \
                    f"{actual_index} instead"

    def _validate_colour(self, embed: discord.Embed, match_all_if_not_set: bool):
        if match_all_if_not_set and self._colour is _MISSING:
            return

        if self._colour is _MISSING or self._colour is None:
            assert embed.colour is None, f"Expected embed colour to be None, but was {embed.colour.value}."
            return

        assert self._colour == embed.colour.value, f"Expected embed colour to be {embed.colour.value}."
