import pytest

import accord
import accord.utils


# noinspection PyMethodMayBeStatic
class EmbedTitleAndDescriptionValidationFeatures:
    
    async def should_see_embeds_from_response(self, accord_engine: accord.Engine):
        await accord_engine.app_command("embed")
        
        assert accord_engine.response.embed.title == "Test embed"
        
    async def should_see_content_from_embed_response(self, accord_engine: accord.Engine):
        await accord_engine.app_command("embed")
        
        assert accord_engine.response.content == "Here's your embed:"

    async def should_be_able_to_create_and_use_embed_verifier_objects(self, accord_engine: accord.Engine):
        description = "An embed for testing embeds"
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match=description)
        
        await accord_engine.app_command("embed")
        
        embed_verifier.matches_fully(accord_engine.response.embed)

    async def should_be_able_to_match_only_configured_fields(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier()
        
        await accord_engine.app_command("embed")
        
        embed_verifier.matches_configured(accord_engine.response.embed)

    async def should_raise_assertion_error_with_message_if_incorrect_title(self, accord_engine: accord.Engine):
        description = "An embed for testing embeds"
        embed_verifier = accord.EmbedVerifier(title_match="Incorrect embed", description_match=description)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected field 'title' to match pattern 'Incorrect embed', but found " + \
                                       "'Test embed' instead."
        
    async def should_raise_assertion_error_with_message_if_incorrect_description(self, accord_engine: accord.Engine):
        description = "Incorrect description"
        actual_description = "An embed for testing embeds"
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match=description)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == f"Expected field 'description' to match pattern '{description}', but found " + \
                                       f"'{actual_description}' instead."


# noinspection PyMethodMayBeStatic
class EmbedAuthorValidationFeatures:
      
    async def should_support_author_validation(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed",
                                              description_match="An embed for testing embeds",
                                              author_name=accord.user.name,
                                              author_icon_url=accord.user.avatar.url,
                                              author_url="http://embed.url")
        
        await accord_engine.app_command("embed", author_info=True)
        
        embed_verifier.matches_fully(accord_engine.response.embed)   
        
    async def should_raise_exception_if_expecting_no_author_name_but_name_present(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed",
                                              description_match="An embed for testing embeds",
                                              author_icon_url=accord.user.avatar.url,
                                              author_url="http://embed.url")
        
        await accord_engine.app_command("embed", author_info=True)
        
        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == f"Expected field 'author.name' to match pattern 'None', but found " \
                                       f"'{accord.user.name}' instead."

    async def should_raise_exception_if_expecting_no_author_icon_but_icon_present(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed",
                                              description_match="An embed for testing embeds",
                                              author_name=accord.user.name,
                                              author_url="http://embed.url")

        await accord_engine.app_command("embed", author_info=True)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == f"Expected field 'author.icon_url' to match pattern 'None', but found " \
                                       f"'{accord.user.avatar.url}' instead."
        
    async def should_raise_exception_if_expecting_no_author_url_but_url_present(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed",
                                              description_match="An embed for testing embeds",
                                              author_name=accord.user.name,
                                              author_icon_url=accord.user.avatar.url)

        await accord_engine.app_command("embed", author_info=True)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected field 'author.url' to match pattern 'None', but found " \
                                       "'http://embed.url' instead."
        
    async def should_pass_if_author_data_present_and_using_matches_configured(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match="An embed for testing embeds")
        
        await accord_engine.app_command("embed", author_info=True)
        
        embed_verifier.matches_configured(accord_engine.response.embed)
        
    async def should_throw_if_none_author_while_expecting_author_name_data(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match="An embed for testing embeds",
                                              author_name="Invalid", author_url=None, author_icon_url=None)
        
        await accord_engine.app_command("embed")
        
        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == "Expected to have author name data in embed but found no author data."

    async def should_throw_if_none_author_while_expecting_author_icon_data(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match="An embed for testing embeds",
                                              author_name=None, author_url=None, author_icon_url=accord.user.avatar.url)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have author icon url data in embed but found no author data."
        
    async def should_throw_if_none_author_while_expecting_author_url_data(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match="An embed for testing embeds",
                                              author_name=None, author_url="https://embed.url", author_icon_url=None)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have author url data in embed but found no author data."
        
    async def should_throw_if_expecting_author_name_on_none_if_icon_and_url_set_as_missing(
            self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match="An embed for testing embeds",
                                              author_name="Invalid")

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have author name data in embed but found no author data."
    
    async def should_throw_if_expecting_author_url_on_none_if_icon_and_name_set_as_missing(
            self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match="An embed for testing embeds",
                                              author_url="https://embed.url")

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have author url data in embed but found no author data."
        
    async def should_throw_if_expecting_author_icon_on_none_if_url_and_name_set_as_missing(
            self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Test embed", description_match="An embed for testing embeds",
                                              author_icon_url=accord.user.avatar.url)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have author icon url data in embed but found no author data."

        
# noinspection PyMethodMayBeStatic
class EmbedFieldsValidationFeatures:

    async def should_be_able_to_add_fields_as_tuples_to_verifier_and_use_them(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1", False), ("2", "Field 2", False)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)
        
        await accord_engine.app_command("fields", amount=2, inline=False)
        
        embed_verifier.matches_fully(accord_engine.response.embed)
        
    async def should_raise_assertion_error_if_incorrect_order_while_matching_fully(self, accord_engine: accord.Engine):
        fields = [("2", "Field 2", False), ("1", "Field 1", False)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=2, inline=False)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == "Expected to find field '2' in index 0, but was in index " \
                                       "1 instead"
        
    async def should_be_able_to_allow_any_order_when_matching_only_configured(self, accord_engine: accord.Engine):
        fields = [("2", "Field 2", False), ("1", "Field 1", False)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=2, inline=False)

        embed_verifier.matches_configured(accord_engine.response.embed, allow_any_field_order=True)
        
    async def should_not_allow_extra_fields_if_matching_fully(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1", True), ("2", "Field 2", True)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=3, inline=True)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == "Expected to find 2 fields in embed, but found 3 fields instead."
        
    async def should_raise_exception_on_missing_field_if_matching_fully(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1", False), ("2", "Field 2", False), ("3", "Field 3", False)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=2, inline=False)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == "Expected to find 3 fields in embed, but found 2 fields instead."
        
    async def should_pluralise_expected_field_amount_correctly(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1", False)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=2, inline=False)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to find 1 field in embed, but found 2 fields instead."

    async def should_pluralise_actual_field_amount_correctly(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1", False), ("2", "Field 2", False)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=1, inline=False)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to find 2 fields in embed, but found 1 field instead."
        
    async def should_raise_if_missing_fields_when_matching_configured_only(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1", False), ("2", "Field 2", False), ("3", "Field 3", False)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=2, inline=False)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_configured(accord_engine.response.embed, allow_any_field_order=True, 
                                              allow_extra_fields=True)

        assert str(exception.value) == "Expected to find field with name '3' and value 'Field 3' with inline set to " \
                                       "False in the embed fields. Fields [0, 1] were ignored because they were used " \
                                       "in earlier verifications."

    async def should_be_able_to_ignore_extra_fields_when_matching_only_configured(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1", True), ("2", "Field 2", True)]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=3, inline=True)

        embed_verifier.matches_configured(accord_engine.response.embed, allow_extra_fields=True)
        
    async def should_be_able_to_ignore_inlining_by_not_providing_a_value(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1"), ("2", "Field 2")]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)
        
        await accord_engine.app_command("fields", amount=2, inline=True)
        await accord_engine.app_command("fields", amount=2, inline=False)
        
        embed_verifier.matches_fully(accord_engine.get_response(0).embed)
        embed_verifier.matches_fully(accord_engine.get_response(1).embed)
    
    async def should_not_give_inline_data_if_field_with_no_inline_data_fails(self, accord_engine: accord.Engine):
        fields = [("1", "Field 1"), ("2", "Field 2")]
        embed_verifier = accord.EmbedVerifier(title_match="Fields test", description_match="Testing embed fields",
                                              fields=fields)

        await accord_engine.app_command("fields", amount=1, inline=False)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_configured(accord_engine.response.embed, allow_any_field_order=True, 
                                              allow_extra_fields=True)

        assert str(exception.value) == "Expected to find field with name '2' and value 'Field 2' in the embed " \
                                       "fields. Fields [0] were ignored because they were used in earlier " \
                                       "verifications."
        

# noinspection PyMethodMayBeStatic
class ColourValidationFeatures:
    
    async def should_be_able_to_validate_embed_colour(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              colour=0x000000)
        
        await accord_engine.app_command("custom-embed", colour=0x000000)
        
        embed_verifier.matches_configured(accord_engine.response.embed)
        
    async def should_be_able_to_validate_none_colour_on_match_configured(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(colour=None)
        
        await accord_engine.app_command("embed")
        
        embed_verifier.matches_configured(accord_engine.response.embed)
        
    async def should_tell_in_error_message_if_wrong_colour_on_validation(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              colour=0x000001)
        
        await accord_engine.app_command("custom-embed", colour=0x000000)
        
        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == "Expected embed colour to be 0x000001, but was 0x000000."
        
    async def should_tell_in_error_message_if_colour_none_expected_on_validation(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              colour=None)

        await accord_engine.app_command("custom-embed", colour=0x000000)

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected embed colour to be None, but was 0x000000."
        
    async def should_tell_in_error_message_if_colour_expected_but_was_none(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(colour=0x000000)

        await accord_engine.app_command("embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_configured(accord_engine.response.embed)

        assert str(exception.value) == "Expected embed colour to be 0x000000, but was None."
        
    async def should_support_spelling_colour_as_color(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              color=0x123456)
        
        await accord_engine.app_command("custom-embed", colour=0x123456)
        
        embed_verifier.matches_fully(accord_engine.response.embed)
        
    async def should_throw_accord_exception_if_both_colour_and_color_set(self):
        with pytest.raises(accord.AccordException) as exception:
            _ = accord.EmbedVerifier(colour=0x000000, color=0x000001)
            
        assert str(exception.value) == "Attempted to set both 'colour' and 'color' fields while creating an embed " \
                                       "verifier. Please only use one of the fields."
        
        
# noinspection PyMethodMayBeStatic
class FooterValidationFeatures:
    
    async def should_allow_validating_footer_text_and_url(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              footer_text="Custom footer",
                                              footer_icon_url="footer.url")
        
        await accord_engine.app_command("custom-embed", footer_text="Custom footer", footer_icon_url="footer.url")
        
        embed_verifier.matches_fully(accord_engine.response.embed)
        
    async def should_throw_if_incorrect_footer_text(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              footer_text="Custom footer",
                                              footer_icon_url="footer.url")

        await accord_engine.app_command("custom-embed", footer_text="Invalid footer", footer_icon_url="footer.url")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)
            
        assert str(exception.value) == "Expected field 'footer.text' to match pattern 'Custom footer', " \
                                       "but found 'Invalid footer' instead."

    async def should_throw_if_incorrect_footer_url(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              footer_text="Custom footer",
                                              footer_icon_url="footer.url")

        await accord_engine.app_command("custom-embed", footer_text="Custom footer", footer_icon_url="invalid.url")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected field 'footer.icon_url' to match pattern 'footer.url', " \
                                       "but found 'invalid.url' instead."
        
    async def should_throw_if_none_footer_while_expecting_footer_text(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              footer_text="Custom footer",
                                              footer_icon_url=None)

        await accord_engine.app_command("custom-embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have footer text data in embed but found no footer data."
        
    async def should_throw_if_none_footer_while_expecting_footer_icon(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              footer_text=None,
                                              footer_icon_url="footer.url")

        await accord_engine.app_command("custom-embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have footer icon url data in embed but found no footer data."
        
    async def should_throw_if_expecting_footer_text_on_none_and_icon_set_as_missing(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              footer_text="Custom footer")

        await accord_engine.app_command("custom-embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have footer text data in embed but found no footer data."
        
    async def should_throw_if_expecting_footer_icon_on_none_and_text_set_as_missing(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(title_match="Custom embed",
                                              description_match="Testing other embed values",
                                              footer_icon_url="footer.url")

        await accord_engine.app_command("custom-embed")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_fully(accord_engine.response.embed)

        assert str(exception.value) == "Expected to have footer icon url data in embed but found no footer data."
        
    async def should_throw_if_expecting_footer_text_and_found_none(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(footer_text="Custom footer")
        
        await accord_engine.app_command("custom-embed", footer_icon_url="footer.url")
        
        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_configured(accord_engine.response.embed)
            
        assert str(exception.value) == "Expected field 'footer.text' to match pattern 'Custom footer', " \
                                       "but found 'None' instead."

    async def should_throw_if_expecting_footer_icon_url_and_found_none(self, accord_engine: accord.Engine):
        embed_verifier = accord.EmbedVerifier(footer_icon_url="footer.url")

        await accord_engine.app_command("custom-embed", footer_text="Custom footer")

        with pytest.raises(AssertionError) as exception:
            embed_verifier.matches_configured(accord_engine.response.embed)

        assert str(exception.value) == "Expected field 'footer.icon_url' to match pattern 'footer.url', " \
                                       "but found 'None' instead."
    