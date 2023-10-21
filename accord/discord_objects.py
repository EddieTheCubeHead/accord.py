from __future__ import annotations

import threading
import typing
from unittest.mock import Mock

import discord


def _create_id():
    latest_id = 0
    id_generator_lock = threading.Lock()
    while True:
        with id_generator_lock:
            latest_id += 1
        yield latest_id


id_generator = _create_id()


class DiscordObject:
    """Base class for mocked discord objects.
    
    Caution:
        You should never instantiate a raw :class:`discord_objects.DiscordObject` manually. Instead, use the 
        ``create_{object}`` methods like :meth:`accord.create_guild` in the main :mod:`accord` module.
    
    Attributes:
        id: The id of the object. Always generated automatically. Not currently in snowflake format, just a raw 
            :class:`int`
    """

    def __init__(self):
        self.id: int = next(id_generator)


class Guild(DiscordObject):
    """A mock discord object representing a :class:`discord.Guild` object.
    
    Caution:
        You should never instantiate a :class:`discord_objects.Guild` object manually. Instead, you should use the
        :meth:`accord.create_guild` method.
    
    Attributes:
        name: The name of the guild
    """
    
    def __init__(self, name: str = None):
        super().__init__()
        self.name: str = name if name is not None else f"Guild {self.id}"
        
    def as_dict(self) -> dict[str, typing.Any]:
        """Gets the guild in dictionary format resembling the guild data sent by discord.
        
        Returns:
            A dict of the guild data
        """
        return {
            "id": self.id,
            "name": self.name
        }


class User(DiscordObject):
    """A mock discord object representing a :class:`discord.User` object.

    Caution:
        You should never instantiate a :class:`discord_objects.User` object manually. Instead, you should use the
        :meth:`accord.create_user` method.

    Attributes:
        name: The username of the user
        avatar: The avatar url of the user
        discriminator: The discriminator of the user. NOTE: we'll have to see how long this lasts
    """
    
    def __init__(self, name: str = None, avatar: str = None, discriminator: str = None):
        super().__init__()
        self.name: str = name if name is not None else f"User {self.id}"
        discord_base = "https://cdn.discordapp.com"
        avatar_url = avatar if avatar is not None else f"{discord_base}/user_{self.id}_avatar.png"
        self.avatar: discord.Asset = Mock(url=avatar_url, key=self.id, BASE=discord_base)
        self.discriminator: str = discriminator if discriminator is not None else str(self.id)
        
    def as_dict(self) -> dict[str, typing.Any]:
        """Gets the user in dictionary format resembling the user data sent by discord.

        Returns:
            A dict of the user data
        """
        
        return {
            "id": self.id,
            "username": self.name,
            "discriminator": self.discriminator,
            "avatar": {
                "url": self.avatar.url,
                "key": self.avatar.key
            }
        }


class Member(DiscordObject):
    """A mock discord object representing a :class:`discord.Member` object.

    Caution:
        You should never instantiate a :class:`discord_objects.Member` object manually. The library creates members
        automatically when a user is used with a guild that the user is not currently a member of.

    Attributes:
        guild: The guild the user is the member of
        user: The user that is the member of the guild
    """

    def __init__(self, guild: Guild, user: User):
        super().__init__()
        self.guild: Guild = guild
        self.user: User = user

    def as_dict(self) -> dict:
        """Gets the member in dictionary format resembling the member data sent by discord.

        Returns:
            A dict of the member data
        """
        return {
            "user": self.user.as_dict()
        }


class TextChannel(DiscordObject):
    """A mock discord object representing a :class:`discord.TextChannel` object.

    Caution:
        You should never instantiate a :class:`discord_objects.TextChannel` object manually. Instead, you should use the
        :meth:`accord.create_text_channel` method.

    Attributes:
        guild: The guild the text channel belongs to
        name: The name of the text channel
    """

    def __init__(self, guild: Guild, name: str = None):
        super().__init__()
        self.guild: Guild = guild
        self.name: str = name if name is not None else f"Text channel {self.id}"

    def as_dict(self) -> dict:
        """Gets the text channel in dictionary format resembling the channel data sent by discord.

        Returns:
            A dict of the channel data
        """
        return {
            "id": self.id,
            "guild_id": self.guild.id
        }


class Message(DiscordObject):
    """A mock discord object representing a :class:`discord.Message` object.

    Caution:
        You should create instantiate a :class:`discord_objects.Message` object. The library creates messages 
            accordingly as a part of it's functionality

    Attributes:
        text_channel: The text channel the message belongs to
        author: The name of the text channel
        interaction: The :mod:`discord.py` :obj:`Interaction` associated with the message if any. :obj:`None` otherwise
    """

    def __init__(self, text_channel: TextChannel, author: Member):
        super().__init__()
        self.text_channel: TextChannel = text_channel
        self.author: Member = author
        self.interaction: discord.Interaction | None = None
