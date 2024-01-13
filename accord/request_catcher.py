from unittest.mock import Mock

from discord import MessageFlags


# noinspection PyProtectedMember
class Response:
    """A class representing a discord.py response internally"""

    def __init__(self, payload: dict):
        self.content = payload["data"]["content"]
        self.flags = MessageFlags._from_value(payload["data"].pop("flags", 0))


class RequestCatcher:

    def __init__(self):
        self._all_responses = []

    def __call__(self, *args, **kwargs):
        self._all_responses.append(Response(kwargs["payload"]))
        return Mock()

    def get_response(self, index: int) -> Response:
        return self._all_responses[index]

    def clear_responses(self):
        self._all_responses.clear()
