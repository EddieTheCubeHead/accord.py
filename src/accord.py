from __future__ import annotations

import asyncio
import inspect
import threading
import typing
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

    def __init__(self, engine: Engine, message: Message, content: str | None, *, ephemeral: bool = False,
                 view: discord.ui.View = None, modal: discord.ui.Modal = None):
        self._engine = engine
        self._message = message
        self.content = str(content)
        self.ephemeral = ephemeral
        self.view = view
        self.modal = modal
        
    @property
    def button(self) -> discord.ui.Button | None:
        return self.get_button()

    async def activate_button(self, button: str | int = 0):
        to_activate = self.get_button(button)
        if to_activate is None:
            return
        interaction = create_component_interaction(self._engine, 3, self._message, to_activate.custom_id)
        self._engine.client._connection._view_store.dispatch_view(2, to_activate.custom_id, interaction)
        await asyncio.sleep(0)
        
    def get_button(self, button: str | int = 0) -> discord.ui.Button | None:
        button_name: str | None = button if type(button) == str else None
        button_index: int | None = button if type(button) == int else None
        all_items = self.view.children
        found_button: discord.ui.Button | None = None
        for index, item in enumerate(all_items):
            if item.type.name != "button":
                continue
            if item.label == button_name or index == button_index:
                found_button = item
                break
        return found_button
    
    def modal_input(self, modal_field: str, value: typing.Any) -> Response:
        field = getattr(self.modal, modal_field)
        if field is None:
            return self

        field._value = value
        for inner_field in self.modal.children:
            if field.custom_id == inner_field.custom_id:
                inner_field._value = value
                break
        return self
    
    async def submit_modal(self):
        modal = self.modal
        interaction = create_component_interaction(self._engine, 5, self._message, modal.custom_id)
        components = _build_components(modal)
        self._engine.client._connection._view_store.dispatch_modal(modal.custom_id, interaction, components)
        await asyncio.sleep(0)
        

def _build_components(modal: discord.ui.Modal) -> list[dict[typing.Any, typing.Any]]:
    child_list = []
    for child in modal.children:
        child_list.append({"value": child.value, "custom_id": child.custom_id, "type": child.type.value})
    components = {"type": 1, "components": child_list}
    return [components]
                
    
class ResponseCatcher:
    
    def __init__(self, parent: discord.Interaction, engine: Engine, text_channel: TextChannel, author: Member,
                 message: Message = None):
        self._parent = parent
        self._engine = engine
        self._message = message if message is not None else Message(text_channel, author)
        self._message.interaction = parent
        self._original_message = message
        self._responded = False
        
    def send_message(self, content: str, *, ephemeral: bool = False, view: discord.ui.View = None):
        if self._responded:
            raise discord.InteractionResponded(self._parent)
        self._responded = True
        response = Response(self._engine, self._message, content, ephemeral=ephemeral, view=view)
        self._engine.all_responses.append(response)
        self._handle_view(view, ephemeral=False)

    # noinspection PyProtectedMember
    def _handle_view(self, view: discord.ui.View | None, ephemeral: bool = False):
        if view is discord.utils.MISSING or view.is_finished():
            return
        
        if ephemeral and view.timeout is None:
            view.timeout = 15 * 60.0

        entity_id = self._parent.id if self._parent.type is discord.enums.InteractionType.application_command else None
        self._engine.client._connection.store_view(view, entity_id)
        
    def send_modal(self, modal: discord.ui.Modal):
        response = Response(self._engine, self._message, None, modal=modal)
        self._engine.all_responses.append(response)
        self._engine.client._connection.store_view(modal)


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
        
        
class Message(DiscordObject):
    
    def __init__(self, text_channel: TextChannel, author: Member):
        super().__init__()
        self.text_channel = text_channel
        self.author = author
        self.interaction: discord.Interaction | None = None


def create_command_interaction(engine: Engine, guild: Guild, member: Member, text_channel: TextChannel,
                               command_name: str, *args, **kwargs) -> discord.Interaction:
    mock_interaction = _create_interaction_base(engine, member, text_channel)
    mock_interaction.command = engine.command_tree.get_command(command_name)
    mock_interaction.type = discord.enums.InteractionType.application_command
    _build_command_interaction_data(mock_interaction, guild, *args, **kwargs)
    return mock_interaction


def create_component_interaction(engine: Engine, type: int, message: Message, component_id: str) -> discord.Interaction:
    mock_interaction = _create_interaction_base(engine, message.author, message.text_channel, message)
    _build_component_interaction_data(mock_interaction, type, component_id)
    return mock_interaction


# mocking properties causes warnings that should be ignored
# noinspection PyPropertyAccess
def _create_interaction_base(engine: Engine, member: Member, text_channel: TextChannel,
                             message: Message = None) -> discord.Interaction:
    mock_interaction: discord.Interaction = AsyncMock(discord.Interaction)
    mock_interaction.id = next(id_generator) if message is None else message.interaction.id
    mock_interaction.guild = text_channel.guild
    mock_interaction.user = member.user
    mock_interaction.channel = text_channel
    mock_interaction.accord_engine = engine
    mock_interaction.response = ResponseCatcher(mock_interaction, engine, text_channel, member, message)
    if message is not None:
        mock_interaction.message = message
    return mock_interaction
    

def _build_command_interaction_data(interaction: discord.Interaction, guild: Guild, *args, **kwargs):
    signature = inspect.signature(interaction.command.callback)
    options = _build_options(signature, *args, **kwargs)
    interaction.data = {"type": 1, "name": interaction.command.name, "guild_id": guild.id, "options": options}
    
    
def _build_component_interaction_data(interaction: discord.Interaction, type: int, custom_id: str):
    interaction.data = {"type": 3, "custom_id": custom_id}
    


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
        self.client = client
        self.command_tree = command_tree
        self.all_responses: list[Response] = []

        guild = Guild()
        self.guilds: dict[int, Guild] = {guild.id: guild}
        self._default_guild_id = guild.id

        user = User()
        self.users: dict[int, User] = {user.id: user}
        self._default_user_id = user.id

        member = Member(guild, user)
        self.members: dict[(int, int), Member] = {(member.user.id, member.guild.id): member}

        text_channel = TextChannel(guild)
        self.text_channels: dict[int, TextChannel] = {text_channel.id: text_channel}
        self._default_text_channel_id = text_channel.id

    @property
    def response(self) -> Response:
        return self.all_responses[-1]

    @property
    def guild(self) -> Guild:
        return self.guilds[self._default_guild_id]

    @property
    def user(self) -> User:
        return self.users[self._default_user_id]

    @property
    def member(self) -> Member:
        return self.members[(self._default_user_id, self._default_guild_id)]

    @property
    def text_channel(self) -> TextChannel:
        return self.text_channels[self._default_text_channel_id]

    async def app_command(self, command_name: str, *args, guild_id: int = None, member_id: int = None,
                          channel_id: int = None, **kwargs):
        event_loop = asyncio.get_running_loop()
        self.client.loop = event_loop
        guild = self.guilds[guild_id] if guild_id is not None else self.guild
        member = self.members[member_id] if member_id is not None else self.member
        text_channel = self.text_channels[channel_id] if channel_id is not None else self.text_channel
        interaction = create_command_interaction(self, guild, member, text_channel, command_name, *args, **kwargs)
        self.command_tree._from_interaction(interaction)
        self.client._connection.dispatch('interaction', interaction)
        await asyncio.sleep(0)

    def get_response(self, index: int) -> Response:
        return self.all_responses[index]

    def clear_responses(self):
        self.all_responses.clear()
