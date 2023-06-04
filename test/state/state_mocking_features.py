import pytest

import accord


# noinspection PyMethodMayBeStatic
class StateMockingFeatures:
    
    async def should_be_able_to_create_and_use_new_guild(self, accord_engine: accord.Engine):
        guild = accord.create_guild()
        await accord_engine.app_command("guild", command_guild=guild)
        
        assert accord_engine.response.content == f"Guild name: {guild.name}"
        
    async def should_be_able_to_name_created_guild(self, accord_engine: accord.Engine):
        guild = accord.create_guild(name="New guild")
        await accord_engine.app_command("guild", command_guild=guild)
        
        assert accord_engine.response.content == "Guild name: New guild"
        
    async def should_be_able_to_call_app_command_on_guild_with_id(self, accord_engine: accord.Engine):
        guild = accord.create_guild()
        await accord_engine.app_command("guild", command_guild=guild.id)
        
        assert accord_engine.response.content == f"Guild name: {guild.name}"
        
    async def should_be_able_to_prevent_default_channel_creation(self):
        guild = accord.create_guild(create_default_channel=False)
        
        assert guild.id not in accord.default_text_channel_ids
  
    async def should_throw_exception_if_no_text_channel_for_guild(self, accord_engine: accord.Engine):
        guild = accord.create_guild(create_default_channel=False)
        
        with pytest.raises(accord.AccordException) as actual_exception:
            await accord_engine.app_command("ping", command_guild=guild)
        assert str(actual_exception.value) == f"Could not find a default text channel for guild '{guild.name}'"
        
    async def should_be_able_to_create_and_use_new_text_channel(self, accord_engine: accord.Engine):
        channel = accord.create_text_channel()
        await accord_engine.app_command("channel", channel=channel)
        
        assert accord_engine.response.content == f"Channel name: {channel.name}"
        
    async def should_be_able_to_name_created_text_channel(self, accord_engine: accord.Engine):
        channel = accord.create_text_channel(name="New channel")
        await accord_engine.app_command("channel", channel=channel)
        
        assert accord_engine.response.content == "Channel name: New channel"
        
    async def should_be_able_to_call_app_command_on_channel_with_id(self, accord_engine: accord.Engine):
        channel = accord.create_text_channel()
        await accord_engine.app_command("channel", channel=channel.id)
        
        assert accord_engine.response.content == f"Channel name: {channel.name}"
        
    async def should_be_able_to_use_custom_guild_and_custom_channel_simultaneously(self, accord_engine: accord.Engine):
        guild = accord.create_guild()
        channel = accord.create_text_channel(guild)
        await accord_engine.app_command("channel-guild", command_guild=guild, channel=channel)
        
        assert accord_engine.response.content == f"Channel name: {channel.name}\n" + \
                                                 f"Guild name: {guild.name}"
