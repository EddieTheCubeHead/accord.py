import discord.ui
import pytest


class ButtonFeatures:
    
    @pytest.mark.asyncio
    async def should_track_button_clicks(self, accord_engine):
        await accord_engine.app_command("button")
        await accord_engine.response.activate_button("Greet")
        
        assert accord_engine.response.content == "Hello there!"
        
    @pytest.mark.asyncio
    async def should_support_button_click_via_view_item_index(self, accord_engine):
        await accord_engine.app_command("buttons")
        await accord_engine.response.activate_button(0)

        assert accord_engine.response.content == "Button 1 clicked"
        
        await accord_engine.get_response(0).activate_button(1)
        
        assert accord_engine.response.content == "Button 2 clicked"
        
    @pytest.mark.asyncio
    async def should_support_shorthand_calls_for_first_button(self, accord_engine):
        await accord_engine.app_command("button")
        await accord_engine.response.activate_button()
        
        assert accord_engine.response.content == "Hello there!"
        
    @pytest.mark.asyncio
    async def should_be_able_to_validate_button_properties(self, accord_engine):
        await accord_engine.app_command("button")
        
        assert isinstance(accord_engine.response.button, discord.ui.Button)
        
    @pytest.mark.asyncio
    async def should_be_able_to_get_button_with_index(self, accord_engine):
        await accord_engine.app_command("buttons", 4)
        
        assert accord_engine.response.get_button(2).label == "3"
        

class ModalFeatures:
    
    @pytest.mark.asyncio
    async def should_see_response_modal_title(self, accord_engine):
        await accord_engine.app_command("modal")
        
        assert accord_engine.response.modal.title == "Example modal"
        
    @pytest.mark.asyncio
    async def should_see_response_modal_fields(self, accord_engine):
        await accord_engine.app_command("modal")
        
        assert accord_engine.response.modal.response.label == "Say something"
        
    @pytest.mark.asyncio
    async def should_support_submitting_modals(self, accord_engine):
        await accord_engine.app_command("modal")
        await accord_engine.response.modal_input("response", "validated").submit_modal()
        
        assert accord_engine.response.content == "validated"

    @pytest.mark.asyncio
    async def should_recognize_raw_input_fields_from_modals(self, accord_engine):
        await accord_engine.app_command("modal", raw_response=True)
        await accord_engine.response.modal_input("response", "validated").submit_modal()

        assert accord_engine.response.content == "validated"
    