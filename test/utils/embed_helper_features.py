import pytest

import accord
import accord.utils


# noinspection PyMethodMayBeStatic
class BasicEmbedValidationFeatures:
    
    async def should_see_embeds_from_response(self, accord_engine: accord.Engine):
        await accord_engine.app_command("embed")
        
        assert accord_engine.response.embed.title == "Test embed"
        
    async def should_see_content_from_embed_response(self, accord_engine: accord.Engine):
        await accord_engine.app_command("embed")
        
        assert accord_engine.response.content == "Here's your embed:"
        
    async def should_be_able_to_create_and_use_embed_verifier_objects(self, accord_engine: accord.Engine):
        description = "An embed for testing embeds"
        embed_verifier = accord.utils.EmbedVerifier(title_match="Test embed", description_match=description)
        
        await accord_engine.app_command("embed")
        
        embed_verifier.matches_fully(accord_engine.response.embed)
        
    async def should_be_able_to_match_only_configured_fields(self, accord_engine: accord.Engine):
        embed_verifier = accord.utils.EmbedVerifier()
        
        await accord_engine.app_command("embed")
        
        embed_verifier.matches_configured(accord_engine.response.embed)

    async def should_raise_assertion_error_with_message_if_incorrect_title(self, accord_engine: accord.Engine):
        description = "An embed for testing embeds"
        embed_verifier = accord.utils.EmbedVerifier(title_match="Incorrect embed", description_match=description)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected field 'title' to match pattern 'Incorrect embed', but found " + \
                                       "'Test embed' instead."
        
    async def should_raise_assertion_error_with_message_if_incorrect_description(self, accord_engine: accord.Engine):
        description = "Incorrect description"
        actual_description = "An embed for testing embeds"
        embed_verifier = accord.utils.EmbedVerifier(title_match="Test embed", description_match=description)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == f"Expected field 'description' to match pattern '{description}', but found " + \
                                       f"'{actual_description}' instead."
    