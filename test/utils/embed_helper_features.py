import accord


# noinspection PyMethodMayBeStatic
class BasicEmbedValidationFeatures:
    
    async def should_see_embeds_from_response(self, accord_engine: accord.Engine):
        await accord_engine.app_command("embed")
        
        assert accord_engine.response.embed.title == "Test embed"
        
    async def should_see_content_from_embed_response(self, accord_engine: accord.Engine):
        await accord_engine.app_command("embed")
        
        assert accord_engine.response.content == "Here's your embed:"
        
    async def should_be_able_to_create_embed_verifier_objects(self, accord_engine: accord.Engine):
        embed_verifier
        
        await accord_engine.app_command("embed")
    