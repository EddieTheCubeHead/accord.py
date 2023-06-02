from unittest.mock import AsyncMock


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
    
    async def should_provide_mocked_guilds_on_startup_if_intent_requested(self, accord_engine: accord.Engine):
        assert accord_engine.client.guilds[0].name == f"Guild {accord.guild.id}"
