import re
import typing

import discord

import accord

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
"""A type representing a tuple containing embed field data.

The first two fields represent the name and value of the field and are mandatory. Last field is optional and represents
the inline-status of the tuple. First two fields are optional strings, the last field should be bool if present.
"""


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
    """A class for verifying embeds created with :mod:`discord.py`

    You can verify that the embed is exactly identical to the constructed verifier object with :meth:`matches_fully` or
    that all configured fields are identical with :meth:`matches_configured`.

    Attention:
        All text-based fields are regex based.
            If you need regex characters, please escape them. Disabling
            regex based validation should be possible at some point in the future.

    Keyword Args:
        title (str | None): The regex validation match for the title of the embed.
        description (str | None): The regex validation match for the description of the embed.
        author_name (str | None): The regex validation match for the name of the author of the embed.
        author_icon_url (str | None): The regex validation match for the icon url of the author of the embed.
        author_url (str | None): The regex validation match for the url of the author of the embed.
        colour (int | None): Numeric validation match for the hex-based colour of the embed.
        color (str | None): US-english based alias for :attr:`colour`
        footer_text (str | None): The regex validation match for the footer text of the embed.
        footer_icon_url (str | None): The regex validation match for the icon url of the footer of the embed.
        image_url (str | None): The regex validation match for the image url of the embed.
        thumbnail_url (str | None): The regex validation match for the thumbnail url of the embed.
        fields (Iterable[EmbedField]): An iterable containing :obj:`EmbedField` tuples representing the fields of the
            embed.
    """
    
    def __init__(self, *, title: str | None = _MISSING, description: str | None = _MISSING,
                 author_name: str | None = _MISSING, author_icon_url: str | None = _MISSING,
                 author_url: str | None = _MISSING, colour: int | None = _MISSING, color: int | None = _MISSING,
                 footer_text: str | None = _MISSING, footer_icon_url: str | None = _MISSING,
                 image_url: str | None = _MISSING, thumbnail_url: str | None = _MISSING,
                 fields: typing.Iterable[EmbedField] | None = _MISSING, ):
        self._title = title
        self._description = description
        self._author_name = author_name
        self._author_icon_url = author_icon_url
        self._author_url = author_url
        self._footer_text = footer_text
        self._footer_icon_url = footer_icon_url
        self._image_url = image_url
        self._thumbnail_url = thumbnail_url
        self._fields = fields
        if colour is _MISSING:
            self._colour = color
        else:
            if color is not _MISSING:
                raise accord.AccordException("Attempted to set both 'colour' and 'color' fields while creating an "
                                             "embed verifier. Please only use one of the fields.")
            self._colour = colour
        
    def matches_fully(self, embed: discord.Embed):
        """A method to verify given embed fully matches the configuration of the :obj:`EmbedVerifier`.

        This means all fields not explicitly set are expected to be :obj:`None` for verification purposes.

        Args:
            embed: The embed to verify.
        """
        self._matches(embed, False, False, False)

    def matches_configured(self, embed: discord.Embed, *, allow_extra_fields: bool = False, 
                           allow_any_field_order: bool = False):
        """A method to verify given embed matches the configured fields of the :obj:`EmbedVerifier`.

        This means all fields not explicitly set are ignored for verification purposes.

        Args:
            embed: The embed to verify.

        Keyword Args:
            allow_extra_fields: Whether more fields are allowed to be present than originally configured. If fields are
                not configured, any number of fields are accepted. Defaults to :obj:`False`
            allow_any_field_order: Whether the configured fields should be allowed to exist in any order. Defaults to
                :obj:`False`
        """
        self._matches(embed, True, allow_extra_fields, allow_any_field_order)

    def _matches(self, embed: discord.Embed, match_all_if_not_set: bool, allow_extra_fields: bool, 
                 allow_any_field_order: bool):
        values = [(_get_pattern(self._title, match_all_if_not_set), embed.title, "title"),
                  (_get_pattern(self._description, match_all_if_not_set), embed.description, "description")]
        if self._validate_author_existence(embed):
            values += [(_get_pattern(self._author_name, match_all_if_not_set), embed.author.name, "author.name"),
                       (_get_pattern(self._author_icon_url, match_all_if_not_set), embed.author.icon_url, 
                        "author.icon_url"),
                       (_get_pattern(self._author_url, match_all_if_not_set), embed.author.url, "author.url")]
        if self._validate_footer_existence(embed):
            values += [(_get_pattern(self._footer_text, match_all_if_not_set), embed.footer.text, "footer.text"),
                       (_get_pattern(self._footer_icon_url, match_all_if_not_set), embed.footer.icon_url, 
                        "footer.icon_url")]
        if self._validate_image_existence(embed):
            values += [(_get_pattern(self._image_url, match_all_if_not_set), embed.image.url, "image.url")]
        if self._validate_thumbnail_existence(embed):
            values += [(_get_pattern(self._thumbnail_url, match_all_if_not_set), embed.thumbnail.url, "thumbnail.url")]
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
        assert self._author_name in (_MISSING, None), "Expected to have author name data in embed but found no " \
                                                      "author data."
        assert self._author_icon_url in (_MISSING, None), "Expected to have author icon url data in embed but found " \
                                                          "no author data."
        assert self._author_url in (_MISSING, None), "Expected to have author url data in embed but found no author " \
                                                     "data."
        
    def _validate_footer_existence(self, embed: discord.Embed) -> bool:
        if not embed.footer:
            self._validate_none_footer()
            return False
        return True
    
    def _validate_none_footer(self):
        assert self._footer_text in (_MISSING, None), "Expected to have footer text data in embed but found no " \
                                                      "footer data."
        assert self._footer_icon_url in (_MISSING, None), "Expected to have footer icon url data in embed but found " \
                                                          "no footer data."

    def _validate_image_existence(self, embed: discord.Embed) -> bool:
        if not embed.image:
            self._validate_none_image()
            return False
        return True

    def _validate_none_image(self):
        assert self._image_url in (_MISSING, None), "Expected to have image url data in embed but found no image data."

    def _validate_thumbnail_existence(self, embed: discord.Embed) -> bool:
        if not embed.thumbnail:
            self._validate_none_thumbnail()
            return False
        return True

    def _validate_none_thumbnail(self):
        assert self._thumbnail_url in (_MISSING, None), "Expected to have thumbnail url data in embed but found no " \
                                                        "thumbnail data."
        
    def _validate_fields(self, embed: discord.Embed, match_all_if_not_set: bool,  allow_extra_fields: bool, 
                         allow_any_order: bool):
        if self._fields is _MISSING:
            self._fields = () if allow_extra_fields else None
        
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
            assert embed.colour is None, f"Expected embed colour to be None, but was 0x{embed.colour.value:06X}."
            return

        assert embed.colour, f"Expected embed colour to be 0x{self._colour:06X}, but was None."
        assert self._colour == embed.colour.value, f"Expected embed colour to be 0x{self._colour:06X}, " \
                                                   f"but was 0x{embed.colour.value:06X}."
