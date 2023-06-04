import pytest

import accord


# noinspection PyMethodMayBeStatic
class StateMockingFeatures:
    
    @pytest.mark.wip
    async def should_be_able_to_create_and_use_new_guild(self, accord_engine: accord.Engine):
        guild = accord.create_guild()
        await accord_engine.app_command("guild", command_guild=guild)
        
        assert accord_engine.response.content == f"Guild id: {guild.id}"
