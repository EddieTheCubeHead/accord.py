from __future__ import annotations

import asyncio
import inspect
import typing
from enum import Enum
from unittest.mock import AsyncMock, Mock, patch, MagicMock

# discord.py wants to be listed as discord.py in requirements, but also wants to be imported as discord
# noinspection PyPackageRequirements
import discord
from discord.gateway import DiscordWebSocket

import accord.discord_objects as discord_objects
from accord.discord_messages import create_app_command_message
from accord.request_catcher import RequestCatcher

guild: discord_objects.Guild = discord_objects.Guild()
"""The default mock guild used for operations with engine.py"""

guilds: dict[int, discord_objects.Guild] = {guild.id: guild}
"""A dictionary containing all created mock guilds, mapped by id"""

default_guild_id: int = guild.id
"""A value containing the id of the default guild"""

user: discord_objects.User = discord_objects.User()
"""The default mock user used for operations with engine.py"""

client_user: discord_objects.User = discord_objects.User("Test client")
"""An user object representing the client being tested"""

users: dict[int, discord_objects.User] = {user.id: user}
"""A dictionary containing all created mock users, mapped by id"""

default_user_id: int = user.id
"""A value containing the id of the default user"""

member: discord_objects.Member = discord_objects.Member(guild, user)
"""A member object based on the relation of the default user and the default guild"""

members: dict[(int, int), discord_objects.Member] = {(member.user.id, member.guild.id): member}
"""A dictionary containing all configured member mappings.

Mapped by a tuple of (user_id, guild_id). A member object is only created when an user is used with a guild for the
first time."""

text_channel: discord_objects.TextChannel = discord_objects.TextChannel(guild)
"""The default mock text channel used for operations with engine.py"""

text_channels: dict[int, discord_objects.TextChannel] = {text_channel.id: text_channel}
"""A dictionary containing all mock text channels, mapped by id"""

default_text_channel_ids: dict[int, int] = {guild.id: text_channel.id}
"""A dictionary containing the default text channel ids for each guild, mapped by guild id"""


class AccordException(Exception):
    """Exception thrown by engine.py, subclasses :class:`Exception` with no interface changes"""
    pass


def create_guild(name: str = None, create_default_channel: bool = True) -> discord_objects.Guild:
    """A method for creating a new mock guild.
    
    Caution:
        You should not instantiate :class:`discord_objects.Guild` manually, instead this method should be used.
    
    Attention:
        Guild id is generated automatically
    
    Args:
        name: The name of the guild to be created. :obj:`None` uses ``Guild {id}``. Defaults to :obj:`None`
        create_default_channel: Whether to create a default text channel for the guild. Defaults to :obj:`True`
        
    Returns:
        The created :class:`discord_objects.Guild` object
    """
    new_guild = discord_objects.Guild(name=name)
    guilds[new_guild.id] = new_guild
    if create_default_channel:
        default_channel = create_text_channel(new_guild)
        default_text_channel_ids[new_guild.id] = default_channel.id
    return new_guild


def create_text_channel(channel_guild: int | discord_objects.Guild = None, name: str = None) \
        -> discord_objects.TextChannel:
    """A method for creating a new mock channel
    
    Caution:
        You should not instantiate :class:`discord_objects.TextChannel` manually, instead this method should be used.
    
    Attention:
        TextChannel id is generated automatically
        
    Args:
        channel_guild: The guild object or the id of the guild the channel should belong to. :obj:`None` uses the 
            default guild (see: :attr:`guild`). Defaults to :obj:`None`
        name: The name of the text channel to be created. :obj:`None` uses ``Text channel {id}``. Defaults to 
            :obj:`None`
        
    Returns:
        The created :class:`discord_objects.TextChannel` object
    """
    channel_guild = guilds[_get_discord_object_id(channel_guild)] if channel_guild is not None else guild
    new_channel = discord_objects.TextChannel(channel_guild, name)
    text_channels[new_channel.id] = new_channel
    return new_channel


def create_user(name: str = None, avatar: str = None, discriminator: str = None):
    """A method for creating a new mock user
    
    Caution:
        You should not instantiate :class:`discord_objects.User` manually, instead this method should be used.
    
    Attention:
        User id is generated automatically
    
    Args:
        name: The name of the user to be created. :obj:`None` uses ``User {id}``. Defaults to :obj:`None`. 
        avatar: The avatar url of the user to be created. :obj:`None` uses ``User {id} avatar``. Defaults to 
            :obj:`None`. 
        discriminator: The discriminator of the user to be created. :obj:`None` uses ``{id}``. Defaults to :obj:`None`. 

    Returns:
        The created :class:`discord_objects.User` object
    """
    new_user = discord_objects.User(name=name, avatar=avatar, discriminator=discriminator)
    users[new_user.id] = new_user
    return new_user


class _InteractionType(Enum):
    ApplicationCommand = 2
    InteractionComponent = 3
    Autocomplete = 4
    ModalSubmit = 5


# The engine will be accessing a lot of the inner workings of discord.py. Suppress warnings for that
# noinspection PyProtectedMember
class Response:
    """A class representing an interaction response sent by the client under testing

    Caution:
        You should not instantiate :class:`accord.Response` yourself.

    Attributes:
        content: The content of the message
        ephemeral: Whether the response is only visible to the user who caused the interaction
        view: The :obj:`discord.ui.View` associated with the response, if any
        modal: The :obj:`discord.ui.Modal` associated with the response, if any
        embed: The :obj:`discord.Embed` associated with the response, if any
    """

    def __init__(self, engine: Engine, message: discord_objects.Message, content: str | None, *,
                 ephemeral: bool = False, view: discord.ui.View = None, modal: discord.ui.Modal = None,
                 embed: discord.Embed = None):
        self._engine = engine
        self._message = message
        self.content = str(content)
        self.ephemeral = ephemeral
        self.view = view
        self.modal = modal
        self.embed = embed

    @property
    def button(self) -> discord.ui.Button | None:
        """A property returning the *first* button of the view associated with the response, if available

        Attention:
            Returns :obj:`None` if response has no view or the view has no buttons.
        """
        return self.get_button()

    async def activate_button(self, button: str | int = 0):
        """A coroutine to activate (click) a button on the view associated with the response.

        Args:
            button: The index or label of the button to activate. Defaults to ``0``
        """
        to_activate = self.get_button(button)
        if to_activate is None:
            return
        interaction = _create_component_interaction(self._engine, 3, self._message, to_activate.custom_id)
        self._engine.client._connection._view_store.dispatch_view(2, to_activate.custom_id, interaction)
        await asyncio.sleep(0)

    def get_button(self, button: str | int = 0) -> discord.ui.Button | None:
        """A method to get a button from the view

        Args:
            button: The index or label of the button to get. Defaults to ``0``

        Returns:
            :obj:`discord_objects.Button` if button found, :obj:`None` if not found.
        """
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
        """A method to send input to a text input field in a modal associated with the response.

        Attention:
            Does nothing if the specified field is not found in the modal

        Args:
            modal_field: the name of the field that should be filled with the given value
            value: The value to be set to the given field

        Returns:
            Returns the :obj:`accord.Response` for chaining
        """
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
        """A coroutine that submits the modal associated with the response."""
        modal = self.modal
        interaction = _create_component_interaction(self._engine, 5, self._message, modal.custom_id)
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
                

# The response catcher will be accessing a lot of the inner workings of discord.py. Suppress warnings for that
# noinspection PyProtectedMember
class _ResponseCatcher:
    
    def __init__(self, parent: discord.Interaction, engine: Engine, channel: discord_objects.TextChannel,
                 author: discord_objects.Member, message: discord_objects.Message = None):
        self._parent = parent
        self._engine = engine
        self._message = message if message is not None else discord_objects.Message(channel, author)
        self._message.interaction = parent
        self._original_message = message
        self._responded = False
        
    def send_message(self, content: str = None, *, ephemeral: bool = False, view: discord.ui.View = None,
                     embed: discord.Embed = None):
        if self._responded:
            raise discord.InteractionResponded(self._parent)
        self._responded = True
        response = Response(self._engine, self._message, content, ephemeral=ephemeral, view=view, embed=embed)
        self._engine._all_responses.append(response)
        self._handle_view(view, ephemeral=False)

    def _handle_view(self, view: discord.ui.View | None, ephemeral: bool = False):
        if view is discord.utils.MISSING or view.is_finished():
            return
        
        if ephemeral and view.timeout is None:
            view.timeout = 15 * 60.0

        entity_id = self._parent.id if self._parent.type is discord.enums.InteractionType.application_command else None
        self._engine.client._connection.store_view(view, entity_id)
        
    def send_modal(self, modal: discord.ui.Modal):
        response = Response(self._engine, self._message, None, modal=modal)
        self._engine._all_responses.append(response)
        self._engine.client._connection.store_view(modal)


def _create_command_interaction(engine: Engine, guild: discord_objects.Guild, member: discord_objects.Member,
                                text_channel: discord_objects.TextChannel, command_name: str, *args, **kwargs) \
        -> discord.Interaction:
    mock_interaction = _create_interaction_base(engine, member, text_channel)
    mock_interaction.command = engine.command_tree.get_command(command_name)
    mock_interaction.type = discord.enums.InteractionType.application_command
    _build_command_interaction_data(mock_interaction, guild, *args, **kwargs)
    return mock_interaction


def _create_component_interaction(engine: Engine, interaction_type: int, message: discord_objects.Message,
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
    mock_interaction.response = _ResponseCatcher(mock_interaction, engine, text_channel, member, message)
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
    """A method to create an :class:`accord.Engine` instance to be used with testing.
    
    Caution:
        You should not instantiate :class:`accord.Engine` manually, instead this method should be used.
        
    Args:
        client: The client that the engine should run against
        command_tree: The command tree of the client
        
    Returns:
        An engine instance that can be used to run commands or events on the client
    """
    engine = Engine(client, command_tree)
    client.ws = DiscordWebSocket(Mock(), loop=client.loop)
    client.ws.shard_id = client.shard_id
    client.ws._discord_parsers = client._connection.parsers
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
    """The engine that is responsible for running commands and events against the client under test.
    
    Caution:
        You should not instantiate :class:`accord.Engine` manually, instead the :meth:`accord.create_engine` method
        should be used.
            
    Attributes:
        client: The client under test
        command_tree: The command tree of the client. Can be :obj:`None` if you are not testing application commands.
    """

    def __init__(self, client: discord.Client, command_tree: discord.app_commands.CommandTree):
        self.client: discord.Client = client
        command_tree.sync = AsyncMock()
        self.command_tree: discord.app_commands.CommandTree | None = command_tree
        self.response_catcher = RequestCatcher()
        self._all_responses: list[Response] = []

    @property
    def response(self) -> Response:
        """A property representing the newest response sent by the client"""
        return self.response_catcher.get_response(-1)

    async def app_command(self, command_name: str,
                          command_guild: int | discord_objects.Guild = None,
                          issuer: int | discord_objects.User = None,
                          channel: int | discord_objects.TextChannel = None, **kwargs):
        """A coroutine to send an application command to the client. 
        
        Attention:
            Accepts *args and **kwargs to be sent to the command.
            
        Raises:
            :exc:`accord.AccordException`: on guild/channel mismatch or if channel is not given and guild does not have
                a default channel
        
        Args:
            command_name: The name of the command to be run
            
        Keyword Args:
            command_guild: The guild or the id of the guild the command should be run on. :obj:`None` uses the default
                guild (see :attr:`guild`). Defaults to :obj:`None`
            issuer: The user or the id of the user issuing the command. :obj:`None` uses the default member (see
                :attr:`member`). Defaults to :obj:`None`
            channel: The channel of the id of the channel the command is issued on. :obj:`None` uses the default text
                channel (see :attr:`text_channel`). Defaults to :obj:`None`
            
        """
        command_guild = _get_command_guild(command_guild)
        issuer = _get_command_issuer(command_guild, issuer)
        command_channel = _get_command_channel(command_guild, channel)
        with patch("discord.webhook.async_.AsyncWebhookAdapter.request", new=self.response_catcher):
            await self.client.ws.received_message(create_app_command_message(command_name, command_guild, issuer,
                                                                             command_channel, **kwargs))
            await asyncio.sleep(0)

    def get_response(self, index: int) -> Response:
        """A method for getting a :obj:`Response` in the specified index
        
        Args:
            index: The index of the response
            
        Returns:
            The :obj:`Response` in the specified index.
        """
        return self.response_catcher.get_response(index)

    def clear_responses(self):
        """A method for clearing the response list"""
        self.response_catcher.clear_responses()
        
        
def _get_discord_object_id(discord_object: discord_objects.DiscordObject | int) -> int:
    if isinstance(discord_object, discord_objects.DiscordObject):
        return discord_object.id
    return discord_object


def _get_command_guild(command_guild: int | discord_objects.Guild = None) -> discord_objects.Guild:
    return guilds[_get_discord_object_id(command_guild)] if command_guild is not None else guild


def _get_command_issuer(command_guild: discord_objects.Guild, issuer: int | discord_objects.User = None) \
        -> discord_objects.Member:
    issuer_user = users[_get_discord_object_id(issuer)] if issuer is not None else user
    if (issuer_user.id, command_guild.id) in members:
        return members[(issuer_user.id, command_guild.id)]
    new_member = discord_objects.Member(guild, issuer_user)
    members[(issuer_user.id, command_guild.id)] = new_member
    return new_member


def _get_command_channel(command_guild: discord_objects.Guild,
                         channel: int | discord_objects.TextChannel = None) -> discord_objects.TextChannel:
    if channel is not None:
        channel = text_channels[_get_discord_object_id(channel)]
        if channel.guild.id != command_guild.id:
            raise AccordException(f"Text channel {channel.name} is not from guild {command_guild.name}")
        return channel
    if command_guild.id not in default_text_channel_ids:
        raise AccordException(f"Could not find a default text channel for guild '{command_guild.name}'")
    command_channel = text_channels[_get_discord_object_id(default_text_channel_ids[command_guild.id])]
    return command_channel
