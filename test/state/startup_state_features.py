from unittest.mock import AsyncMock

import discord

import accord


# noinspection PyMethodMayBeStatic
class StartupRunMethodsFeatures:

    async def should_run_on_ready_on_engine_initialization_completion(self, accord_engine: accord.Engine, capsys):
        assert capsys.readouterr().out == "Connected\n"
        
    async def should_run_setup_hook_on_engine_initialization(self, accord_engine: accord.Engine):
        # we have mocked sync using AsyncMock. Type checker is wrong
        # noinspection PyTypeChecker
        sync_function: AsyncMock = accord_engine.command_tree.sync
        assert sync_function.await_args[1]["guild"].id == accord.guild.id
        

# noinspection PyMethodMayBeStatic
class StartupProvideStateFeatures:
    
    async def should_provide_guilds_on_startup_if_intent_requested(self, accord_engine: accord.Engine):
        assert accord_engine.client.guilds[0].name == f"Guild {accord.guild.id}"
        
    async def should_not_provide_guild_on_startup_if_intent_not_present(self):
        intents = discord.Intents.none()
        # We cannot do global import of bot due to monkey patching guild id being required
        from testbot.bot_main import Bot
        bot = Bot("Test bot", intents, discord.Object(accord.guild.id))
        accord_engine = await accord.create_engine(bot, bot.tree)
        
        assert len(accord_engine.client.guilds) == 0
        
    async def should_provide_bot_user_data_on_startup(self, accord_engine: accord.Engine):
        assert accord_engine.client.user.id == accord.client_user.id
        assert accord_engine.client.user.name == accord.client_user.name
