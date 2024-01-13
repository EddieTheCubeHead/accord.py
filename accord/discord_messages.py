from enum import Enum
from json import dumps
from typing import Any

from accord.discord_objects import Member, TextChannel, Guild


class MessageEvent(Enum):
    INTERACTION_CREATE = "INTERACTION_CREATE"


class DiscordOperation(Enum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE = 3
    VOICE_STATE = 4
    VOICE_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_MEMBERS = 8
    INVALIDATE_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
    GUILD_SYNC = 12


class InteractionType(Enum):
    APP_COMMAND = 2


def _create_event_message(event: MessageEvent, operation: DiscordOperation, data: dict) -> str:
    return dumps({
        "t": event.value,
        "op": operation.value,
        "s": 1,  # This doesn't seem to affect anything, edit if problems arise
        "d": data
    })


def create_app_command_message(command_name: str, guild: Guild, member: Member, channel: TextChannel, **kwargs)\
        -> str:
    data = {
        "member": member.as_dict(),
        "guild": guild.as_dict(),
        "data": {
            "name": command_name,
            "options": [create_app_command_option(name, data) for name, data in kwargs.items()]
        },
        "channel_id": channel.id,
        "channel": channel.as_dict(),
        "id": 1,  # This doesn't seem to affect anything, edit if problems arise
        "type": InteractionType.APP_COMMAND.value,
        "token": "MOCK_TOKEN",
        "version": 1,
        "application_id": 1
    }
    return _create_event_message(MessageEvent.INTERACTION_CREATE, DiscordOperation.DISPATCH, data)


def create_app_command_option(name: str, data: Any) -> {str: Any}:
    return {
        "name": name,
        "type": get_app_command_option_type(data),
        "value": data
    }


def get_app_command_option_type(data: Any):
    if type(data) is str:
        return 3
    elif type(data) is int:
        return 4
    elif type(data) is bool:
        return 5
