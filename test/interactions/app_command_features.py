

# noinspection PyMethodMayBeStatic
class BasicAppCommandFeatures:

    async def should_see_command_response_text(self, accord_engine):
        await accord_engine.app_command("ping")

        assert accord_engine.response.content == "pong"

    async def should_see_command_response_ephemeral_status(self, accord_engine):
        await accord_engine.app_command("ping")

        assert not accord_engine.response.ephemeral

        await accord_engine.app_command("ephemeral")

        assert accord_engine.response.ephemeral

    async def should_store_older_responses(self, accord_engine):
        await accord_engine.app_command("ephemeral")
        await accord_engine.app_command("ping")

        assert accord_engine.get_response(index=0).content == "ephemeral"
        assert accord_engine.get_response(index=1).content == "pong"
        assert accord_engine.response.content == "pong"

    async def should_allow_clearing_responses(self, accord_engine):
        await accord_engine.app_command("ephemeral")
        await accord_engine.app_command("ping")
        accord_engine.clear_responses()
        await accord_engine.app_command("ping")

        assert accord_engine.get_response(index=0).content == "pong"
        assert accord_engine.response.content == "pong"

    async def should_allow_passing_basic_arguments(self, accord_engine):
        await accord_engine.app_command("repeat", "test", 3)

        assert accord_engine.response.content == "test\ntest\ntest\n"

    async def should_support_default_values_for_arguments(self, accord_engine):
        await accord_engine.app_command("repeat", "text")

        assert accord_engine.response.content == "text\ntext\n"

    async def should_allow_passing_arguments_with_keywords(self, accord_engine):
        await accord_engine.app_command("repeat", times=3, to_repeat="word")

        assert accord_engine.response.content == "word\nword\nword\n"

    async def should_utilize_transformers(self, accord_engine):
        await accord_engine.app_command("reverse", "example")

        assert accord_engine.response.content == "elpmaxe"

    async def should_utilize_transformers_for_keyword_arguments(self, accord_engine):
        await accord_engine.app_command("reverse", to_reverse="keyword")

        assert accord_engine.response.content == "drowyek"
