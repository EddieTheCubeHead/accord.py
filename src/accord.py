from __future__ import annotations

import asyncio
import inspect
import typing
from enum import Enum
from unittest.mock import AsyncMock

# discord.py wants to be listed as discord.py in requirements, but also wants to be imported as discord
# noinspection PyPackageRequirements
import discord

import discord_objects

guild = discord_objects.Guild()
guilds: dict[int, discord_objects.Guild] = {guild.id: guild}
default_guild_id = guild.id

user = discord_objects.User()
client_user = discord_objects.User("Test client")
users: dict[int, discord_objects.User] = {user.id: user}
default_user_id = user.id

member = discord_objects.Member(guild, user)
members: dict[(int, int), discord_objects.Member] = {(member.user.id, member.guild.id): member}

text_channel = discord_objects.TextChannel(guild)
text_channels: dict[int, discord_objects.TextChannel] = {text_channel.id: text_channel}
default_text_channel_id = text_channel.id


class InteractionType(Enum):
    ApplicationCommand = 2
    InteractionComponent = 3
    Autocomplete = 4
    ModalSubmit = 5


# The engine will be accessing a lot of the inner workings of discord.py. Suppress warnings for that
# noinspection PyProtectedMember
class Response:

    def __init__(self, engine: Engine, message: discord_objects.Message, content: str | None, *, 
                 ephemeral: bool = False, view: discord.ui.View = None, modal: discord.ui.Modal = None):
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
            if item.type != discord.ComponentType.button or not isinstance(item, discord.ui.Button):
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
            if isinstance(inner_field, discord.ui.TextInput) and field.custom_id == inner_field.custom_id:
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
        if isinstance(child, discord.ui.TextInput):
            child_list.append({"value": child.value, "custom_id": child.custom_id, "type": child.type.value})
    components = {"type": 1, "components": child_list}
    return [components]
                
    
class ResponseCatcher:
    
    def __init__(self, parent: discord.Interaction, engine: Engine, text_channel: discord_objects.TextChannel, 
                 author: discord_objects.Member, message: discord_objects.Message = None):
        self._parent = parent
        self._engine = engine
        self._message = message if message is not None else discord_objects.Message(text_channel, author)
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


def create_command_interaction(engine: Engine, guild: discord_objects.Guild, member: discord_objects.Member, 
                               text_channel: discord_objects.TextChannel, command_name: str, *args, **kwargs) \
        -> discord.Interaction:
    mock_interaction = _create_interaction_base(engine, member, text_channel)
    mock_interaction.command = engine.command_tree.get_command(command_name)
    mock_interaction.type = discord.enums.InteractionType.application_command
    _build_command_interaction_data(mock_interaction, guild, *args, **kwargs)
    return mock_interaction


def create_component_interaction(engine: Engine, interaction_type: int, message: discord_objects.Message, 
                                 component_id: str) -> discord.Interaction:
    mock_interaction = _create_interaction_base(engine, message.author, message.text_channel, message)
    _build_component_interaction_data(mock_interaction, interaction_type, component_id)
    return mock_interaction


# mocking properties causes warnings that should be ignored
# noinspection PyPropertyAccess
def _create_interaction_base(engine: Engine, member: discord_objects.Member, text_channel: discord_objects.TextChannel,
                             message: discord_objects.Message = None) -> discord.Interaction:
    mock_interaction: discord.Interaction = AsyncMock(discord.Interaction)
    mock_interaction.id = next(discord_objects.id_generator) if message is None else message.interaction.id
    mock_interaction.guild = text_channel.guild
    mock_interaction.user = member.user
    mock_interaction.channel = text_channel
    mock_interaction.accord_engine = engine
    mock_interaction.response = ResponseCatcher(mock_interaction, engine, text_channel, member, message)
    if message is not None:
        mock_interaction.message = message
    return mock_interaction
    

def _build_command_interaction_data(interaction: discord.Interaction, guild: discord_objects.Guild, *args, **kwargs):
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
async def create_engine(client: discord.Client, command_tree: discord.app_commands.CommandTree) -> Engine:
    engine = Engine(client, command_tree)
    await engine.client._async_setup_hook()
    await engine.client.setup_hook()
    _insert_objects(client)
    engine.client._connection.dispatch("ready")
    await asyncio.sleep(0)
    return engine


# The engine will be accessing a lot of the inner workings of discord.py. Suppress warnings for that
# noinspection PyProtectedMember
def _insert_objects(client: discord.Client):
    discord_client_user = discord.ClientUser(state=client._connection, data=client_user.as_dict())
    client._connection.user = discord_client_user
    # Funnily enough this is ignored in the discord.py source code we're imitating as well
    # noinspection PyTypeChecker
    client._connection._users[discord_client_user.id] = discord_client_user
    if client.intents.guilds:
        for guild_data in guilds.values():
            client._connection._add_guild_from_data(guild_data.as_dict())


# The engine will be accessing a lot of the inner workings of discord.py. Suppress warnings for that
# noinspection PyProtectedMember
class Engine:

    def __init__(self, client: discord.Client, command_tree: discord.app_commands.CommandTree):
        self.client = client
        command_tree.sync = AsyncMock()
        self.command_tree = command_tree
        self.all_responses: list[Response] = []

    @property
    def response(self) -> Response:
        return self.all_responses[-1]

    async def app_command(self, command_name: str, *args, guild_id: int = None, member_id: int = None,
                          channel_id: int = None, **kwargs):
        command_guild = guilds[guild_id] if guild_id is not None else guild
        command_issuer = members[member_id] if member_id is not None else member
        command_channel = text_channels[channel_id] if channel_id is not None else text_channel
        interaction = create_command_interaction(self, command_guild, command_issuer, command_channel, command_name, 
                                                 *args, **kwargs)
        self.command_tree._from_interaction(interaction)
        self.client._connection.dispatch('interaction', interaction)
        await asyncio.sleep(0)

    def get_response(self, index: int) -> Response:
        return self.all_responses[index]

    def clear_responses(self):
        self.all_responses.clear()
