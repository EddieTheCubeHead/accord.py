from __future__ import annotations

import threading

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
    
    def __init__(self):
        super().__init__()
        self.name = f"Guild {self.id}"


class User(DiscordObject):
    pass


class Member(DiscordObject):

    def __init__(self, guild: Guild, user: User):
        super().__init__()
        self.guild = guild
        self.user = user


class TextChannel(DiscordObject):

    def __init__(self, guild: Guild):
        super().__init__()
        self.guild = guild


class Message(DiscordObject):

    def __init__(self, text_channel: TextChannel, author: Member):
        super().__init__()
        self.text_channel = text_channel
        self.author = author
        self.interaction: discord.Interaction | None = None
