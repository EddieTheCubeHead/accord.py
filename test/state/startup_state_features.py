# noinspection PyMethodMayBeStatic
class StartupRunMethodsFeatures:

    async def should_run_on_ready_on_engine_initialization_completion(self, accord_engine, capsys):
        assert capsys.readouterr().out == "Connected\n"
        
    async def should_run_setup_hook_on_engine_initialization(self, accord_engine):
        accord_engine.client.tree.sync.assert_called()
