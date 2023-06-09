import pytest

import accord


def _get_user_command_content(user: accord.User) -> str:
    return f"User name: {user.name}\n" + \
           f"User avatar url: {user.avatar.url}" + \
           f"User discriminator: {user.discriminator}"
    

# noinspection PyMethodMayBeStatic
class GuildMockingFeatures:
    
    async def should_be_able_to_create_and_use_new_guild(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild()
        await accord_engine.app_command("guild", command_guild=guild)
        
        assert accord_engine.response.content == f"Guild name: {guild.name}"
        
    async def should_be_able_to_name_created_guild(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild(name="New guild")
        await accord_engine.app_command("guild", command_guild=guild)
        
        assert accord_engine.response.content == "Guild name: New guild"
        
    async def should_get_created_guild_name_from_id_if_not_defined(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild()
        await accord_engine.app_command("guild", command_guild=guild)
        
        assert accord_engine.response.content == f"Guild name: Guild {guild.id}"
        
    async def should_be_able_to_call_app_command_on_guild_with_id(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild()
        await accord_engine.app_command("guild", command_guild=guild.id)
        
        assert accord_engine.response.content == f"Guild name: {guild.name}"
        
    async def should_be_able_to_prevent_default_channel_creation(self):
        guild: accord.Guild = accord.create_guild(create_default_channel=False)
        
        assert guild.id not in accord.default_text_channel_ids
  
    async def should_throw_exception_if_no_text_channel_for_guild(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild(create_default_channel=False)
        
        with pytest.raises(accord.AccordException) as actual_exception:
            await accord_engine.app_command("ping", command_guild=guild)
        assert str(actual_exception.value) == f"Could not find a default text channel for guild '{guild.name}'"


# noinspection PyMethodMayBeStatic
class TextChannelMockingFeatures:
        
    async def should_be_able_to_create_and_use_new_text_channel(self, accord_engine: accord.Engine):
        channel: accord.TextChannel = accord.create_text_channel()
        await accord_engine.app_command("channel", channel=channel)
        
        assert accord_engine.response.content == f"Channel name: {channel.name}"
        
    async def should_be_able_to_name_created_text_channel(self, accord_engine: accord.Engine):
        channel: accord.TextChannel = accord.create_text_channel(name="New channel")
        await accord_engine.app_command("channel", channel=channel)
        
        assert accord_engine.response.content == "Channel name: New channel"
        
    async def should_get_text_channel_name_from_id_if_not_defined(self, accord_engine: accord.Engine):
        channel: accord.TextChannel = accord.create_text_channel()
        await accord_engine.app_command("channel", channel=channel)
        
        assert accord_engine.response.content == f"Channel name: Text channel {channel.id}"
        
    async def should_be_able_to_call_app_command_on_channel_with_id(self, accord_engine: accord.Engine):
        channel: accord.TextChannel = accord.create_text_channel()
        await accord_engine.app_command("channel", channel=channel.id)
        
        assert accord_engine.response.content == f"Channel name: {channel.name}"
        
    async def should_be_able_to_create_channel_from_custom_guild(self):
        guild: accord.Guild = accord.create_guild()
        channel: accord.TextChannel = accord.create_text_channel(channel_guild=guild)
        
        # The library should be designed to not require deep equivalence here, so only compare ids
        assert channel.guild.id == guild.id
        
    async def should_get_guild_from_global_default_guild_if_not_provided(self):
        channel: accord.TextChannel = accord.create_text_channel()

        # The library should be designed to not require deep equivalence here, so only compare ids.
        assert channel.guild.id == accord.guild.id
        
    async def should_be_able_to_use_custom_guild_and_custom_channel_simultaneously(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild()
        channel: accord.TextChannel = accord.create_text_channel(guild)
        await accord_engine.app_command("channel", command_guild=guild, channel=channel)
        
        assert accord_engine.response.content == f"Channel name: {channel.name}"
        
    async def should_raise_exception_when_channel_not_from_used_guild(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild()
        
        with pytest.raises(accord.AccordException) as exception:
            await accord_engine.app_command("ping", command_guild=guild, channel=accord.text_channel)
        assert str(exception.value) == f"Text channel {accord.text_channel.name} is not from guild {guild.name}"


# noinspection PyMethodMayBeStatic
class UserMockingFeatures:
        
    async def should_be_able_to_create_and_use_new_user(self, accord_engine: accord.Engine):
        user: accord.User = accord.create_user()
        await accord_engine.app_command("user", issuer=user)
        
        assert accord_engine.response.content == _get_user_command_content(user)
        
    async def should_be_able_to_provide_user_data(self, accord_engine: accord.Engine):
        user: accord.User = accord.create_user(name="Tester", avatar="test_icon.png", discriminator="1234")
        await accord_engine.app_command("user", issuer=user)
        
        assert accord_engine.response.content == _get_user_command_content(user)
        
    async def should_get_user_name_icon_and_discriminator_from_id_if_not_provided(self, accord_engine: accord.Engine):
        user: accord.User = accord.create_user()
        await accord_engine.app_command("user", issuer=user)
        
        discord_url = "https://cdn.discordapp.com"
        assert accord_engine.response.content == f"User name: User {user.id}\n" + \
                                                 f"User avatar url: {discord_url}/user_{user.id}_avatar.png" + \
                                                 f"User discriminator: {user.id}"
        
    async def should_be_able_to_reference_command_issuer_by_user_id(self, accord_engine: accord.Engine):
        user: accord.User = accord.create_user()
        await accord_engine.app_command("user", issuer=user.id)
        
        assert accord_engine.response.content == _get_user_command_content(user)
        
    async def should_allow_using_custom_guild_and_channel_with_custom_user(self, accord_engine: accord.Engine):
        guild: accord.Guild = accord.create_guild()
        channel: accord.TextChannel = accord.create_text_channel(guild)
        user: accord.User = accord.create_user()
        await accord_engine.app_command("user", command_guild=guild, channel=channel, issuer=user)
        
        assert accord_engine.response.content == _get_user_command_content(user)
