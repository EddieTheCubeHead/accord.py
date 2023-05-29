from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock

import discord


class Response:

    def __init__(self, message: str, *, ephemeral=False):
        self.message = message
        self.ephemeral = ephemeral

    def text_is(self, text: str) -> bool:
        return text == self.message


def create_mock_interaction(engine: Engine) -> discord.Interaction:
    mock_interaction = AsyncMock()
    mock_interaction.__engine = engine
    mock_interaction.response.send_message.side_effect = mock_interaction.__engine.send_message
    return mock_interaction


class Engine:

    def __init__(self, client: discord.Client, command_tree: discord.app_commands.CommandTree):
        self._client = client
        self._command_tree = command_tree
        self._all_responses: list[Response] = []

    @property
    def response(self) -> Response:
        return self._all_responses[-1]

    def send_message(self, message: str, *, ephemeral=False):
        self._all_responses.append(Response(message, ephemeral=ephemeral))

    async def app_command(self, command_name: str, *args, **kwargs):
        command = self._command_tree.get_command(command_name)
        await command.callback(create_mock_interaction(self), *args, **kwargs)

    def get_response(self, index: int) -> Response:
        return self._all_responses[index]

    def clear_responses(self):
        self._all_responses.clear()
