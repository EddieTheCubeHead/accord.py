import pytest


class TestViews:
    
    @pytest.mark.asyncio
    async def should_track_button_clicks(self, accord_engine):
        await accord_engine.app_command("button")
        await accord_engine.response.activate_button("Greet")
        
        assert accord_engine.response.text == "Hello there!"
        
    @pytest.mark.asyncio
    @pytest.mark.wip
    async def should_support_button_click_via_view_item_index(self, accord_engine):
        await accord_engine.app_command("button")
        await accord_engine.response.activate_button(0)

        assert accord_engine.response.text == "Hello there!"
