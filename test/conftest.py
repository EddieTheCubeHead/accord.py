import pytest

import accord
from testbot.bot_main import bot


@pytest.fixture
async def accord_engine(capsys):
    engine = await accord.create_engine(bot, bot.tree)
    return engine
