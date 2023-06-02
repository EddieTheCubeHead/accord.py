import pytest

import accord


@pytest.fixture
async def accord_engine(capsys, monkeypatch) -> accord.Engine:
    # important to mock GUILD_ID before importing bot
    monkeypatch.setenv("GUILD_ID", accord.guild.id)
    from testbot.bot_main import bot
    engine = await accord.create_engine(bot, bot.tree)
    return engine
