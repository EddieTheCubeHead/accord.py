from __future__ import annotations

import threading
import typing

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

    def __init__(self):
        self.id = next(id_generator)


class Guild(DiscordObject):
    
    def __init__(self, name: str = None):
        super().__init__()
        self.name = name if name is not None else f"Guild {self.id}"
        
    def as_dict(self) -> dict[str, typing.Any]:
        return {
            "id": self.id,
            "name": self.name
        }


class User(DiscordObject):
    
    def __init__(self, name: str = None, avatar: str = None):
        super().__init__()
        self.name = name if name is not None else f"User {self.id}"
        self.avatar = avatar if avatar is not None else f"User {self.id} avatar"
        
    def as_dict(self) -> dict[str, typing.Any]:
        return {
            "id": self.id,
            "username": self.name,
            "discriminator": self.id,
            "avatar": self.avatar
        }


class Member(DiscordObject):

    def __init__(self, guild: Guild, user: User):
        super().__init__()
        self.guild = guild
        self.user = user


class TextChannel(DiscordObject):

    def __init__(self, guild: Guild, name: str = None):
        super().__init__()
        self.guild = guild
        self.name = name if name is not None else f"Text channel {self.id}"


class Message(DiscordObject):

    def __init__(self, text_channel: TextChannel, author: Member):
        super().__init__()
        self.text_channel = text_channel
        self.author = author
        self.interaction: discord.Interaction | None = None
