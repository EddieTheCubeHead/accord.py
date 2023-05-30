from __future__ import annotations

import asyncio
import inspect
import threading
from enum import Enum
from unittest.mock import AsyncMock

import discord


def _create_id():
    latest_id = 0
    id_generator_lock = threading.Lock()
    while True:
        with id_generator_lock:
            latest_id += 1
        yield latest_id


id_generator = _create_id()


class InteractionType(Enum):
    ApplicationCommand = 2
    InteractionComponent = 3
    Autocomplete = 4
    ModalSubmit = 5


class DiscordObject:

    def __init__(self):
        self.id = next(id_generator)


class Response:

    def __init__(self, text: str, *, ephemeral=False):
        self.text = text
        self.ephemeral = ephemeral


class Guild(DiscordObject):
    pass


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


# mocking properties causes warnings that should be ignored
# noinspection PyPropertyAccess
def create_mock_interaction(engine: Engine, guild: Guild, member: Member, text_channel: TextChannel,
                            command_name: str, *args, **kwargs) -> discord.Interaction:
    mock_interaction: discord.Interaction = AsyncMock(discord.Interaction)
    mock_interaction.guild = guild
    mock_interaction.user = member.user
    mock_interaction.channel_id = text_channel.id
    mock_interaction.accord_engine = engine
    mock_interaction.command = engine.command_tree.get_command(command_name)
    _build_interaction_data(mock_interaction, guild, *args, **kwargs)
    mock_interaction.response.send_message.side_effect = mock_interaction.accord_engine.send_message
    return mock_interaction


def _build_interaction_data(interaction: discord.Interaction, guild: Guild, *args, **kwargs):
    signature = inspect.signature(interaction.command.callback)
    options = _build_options(signature, *args, **kwargs)
    interaction.data = {"type": 1, "name": interaction.command.name, "guild_id": guild.id, "options": options}


def _build_options(signature: inspect.Signature, *args, **kwargs):
    options = []
    expected = list(signature.parameters.values())[1:]
    for param, arg in zip(expected, args):
        options.append({"value": arg, "type": 3, "name": param.name})
    for name, value in kwargs.items():
        options.append({"value": value, "type": 3, "name": name})
    return options


# The engine will be accessing a lot of the inner workings of discord.py. Suppress warnings for that
# noinspection PyProtectedMember
class Engine:

    def __init__(self, client: discord.Client, command_tree: discord.app_commands.CommandTree):
        self._client = client
        self.command_tree = command_tree
        self._all_responses: list[Response] = []

        guild = Guild()
        self._guilds: dict[int, Guild] = {guild.id: guild}
        self._default_guild_id = guild.id

        user = User()
        self._users: dict[int, User] = {user.id: user}
        self._default_user_id = user.id

        member = Member(guild, user)
        self._members: dict[int, Member] = {member.id: member}
        self._default_member_id = member.id

        text_channel = TextChannel(guild)
        self._text_channels: dict[int, TextChannel] = {text_channel.id: text_channel}
        self._default_text_channel_id = text_channel.id

    @property
    def response(self) -> Response:
        return self._all_responses[-1]

    @property
    def guild(self) -> Guild:
        return self._guilds[self._default_guild_id]

    @property
    def user(self) -> User:
        return self._users[self._default_user_id]

    @property
    def member(self) -> Member:
        return self._members[self._default_member_id]

    @property
    def text_channel(self) -> TextChannel:
        return self._text_channels[self._default_text_channel_id]

    def send_message(self, message: str, *, ephemeral=False):
        self._all_responses.append(Response(message, ephemeral=ephemeral))

    async def app_command(self, command_name: str, *args, guild_id: int = None, member_id: int = None,
                          channel_id: int = None, **kwargs):
        event_loop = asyncio.get_running_loop()
        self._client.loop = event_loop
        guild = self._guilds[guild_id] if guild_id is not None else self.guild
        member = self._members[member_id] if member_id is not None else self.member
        text_channel = self._text_channels[channel_id] if channel_id is not None else self.text_channel
        interaction = create_mock_interaction(self, guild, member, text_channel, command_name, *args, **kwargs)
        self.command_tree._from_interaction(interaction)
        self._client._connection.dispatch('interaction', interaction)
        await asyncio.sleep(0)

    def get_response(self, index: int) -> Response:
        return self._all_responses[index]

    def clear_responses(self):
        self._all_responses.clear()
