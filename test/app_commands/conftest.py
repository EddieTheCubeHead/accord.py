import pytest

import accord
from bot.bot_main import bot


@pytest.fixture
def accord_engine():
    return accord.Engine(bot, bot.tree)
