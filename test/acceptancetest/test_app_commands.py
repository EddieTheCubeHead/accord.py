import pytest

import accord
from acceptancetest.bot.bot_main import bot


@pytest.fixture
def accord_engine():
    return accord.Engine(bot, bot.tree)


class TestBasicAppCommands:

    @pytest.mark.asyncio
    async def should_see_command_response_text(self, accord_engine):
        await accord_engine.app_command("ping")

        assert accord_engine.response.text_is("pong")

    @pytest.mark.asyncio
    async def should_see_command_response_ephemeral_status(self, accord_engine):
        await accord_engine.app_command("ping")

        assert not accord_engine.response.ephemeral

        await accord_engine.app_command("ephemeral")

        assert accord_engine.response.ephemeral

    @pytest.mark.asyncio
    async def should_store_older_responses(self, accord_engine):
        await accord_engine.app_command("ephemeral")
        await accord_engine.app_command("ping")

        assert accord_engine.get_response(index=0).text_is("ephemeral")
        assert accord_engine.get_response(index=1).text_is("pong")
        assert accord_engine.response.text_is("pong")

    @pytest.mark.asyncio
    async def should_allow_clearing_responses(self, accord_engine):
        await accord_engine.app_command("ephemeral")
        await accord_engine.app_command("ping")
        accord_engine.clear_responses()
        await accord_engine.app_command("ping")

        assert accord_engine.get_response(index=0).text_is("pong")
        assert accord_engine.response.text_is("pong")

    @pytest.mark.asyncio
    async def should_allow_passing_basic_arguments(self, accord_engine):
        await accord_engine.app_command("repeat", "text")

        assert accord_engine.response.text_is("text\ntext\n")

        await accord_engine.app_command("repeat", "test", 3)

        assert accord_engine.response.text_is("test\ntest\ntest\n")

