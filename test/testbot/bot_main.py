import json
import os

# discord.py wants to be listed as discord.py in requirements, but also wants to be imported as discord
# noinspection PyPackageRequirements
from discord import Client, Intents, Object, Interaction
# noinspection PyPackageRequirements
from discord.app_commands import CommandTree, Transform, Transformer
# noinspection PyPackageRequirements
from discord.ui import View, Button, Modal, TextInput


class Bot(Client):
    def __init__(self, description: str, intents: Intents, guild: Object):
        super().__init__(description=description, intents=intents)
        self.tree = CommandTree(self)
        self._guild = guild

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self._guild)
        await self.tree.sync(guild=self._guild)


def _get_secret(secret_name: str) -> str | int:
    secret = os.getenv(secret_name, None)
    if secret is None:
        file_path = os.path.join(os.path.dirname(__file__), "secrets.json")
        with open(file_path, "r", encoding="utf-8") as setting_file:
            secret = json.loads(setting_file.read())[secret_name]
    return secret


def setup_bot() -> Bot:
    guild = Object(id=_get_secret("GUILD_ID"))
    intents = Intents.default()
    intents.members = True
    return Bot("Add description", intents, guild)


bot = setup_bot()


@bot.event
async def on_ready():
    print("Connected")


@bot.tree.command(name="ping")
async def ping(interaction: Interaction):
    await interaction.response.send_message("pong")


@bot.tree.command(name="ephemeral")
async def ephemeral(interaction: Interaction):
    await interaction.response.send_message("ephemeral", ephemeral=True)
    
    
@bot.tree.command(name="guild")
async def guild(interaction: Interaction):
    await interaction.response.send_message(f"Guild name: {interaction.guild.name}")
    
    
@bot.tree.command(name="channel")
async def channel(interaction: Interaction):
    await interaction.response.send_message(f"Channel name: {interaction.channel.name}")
    
    
@bot.tree.command(name="user")
async def user(interaction: Interaction):
    content = f"User name: {interaction.user.name}\n" + \
              f"User avatar: {interaction.user.avatar}" + \
              f"User discriminator: {interaction.user.discriminator}"
        
    await interaction.response.send_message(content)


@bot.tree.command(name="repeat")
async def repeat(interaction: Interaction, to_repeat: str, times: int = 2):
    await interaction.response.send_message(f"{to_repeat}\n" * times)


class Reverser(Transformer):
    async def transform(self, _: Interaction, string: str) -> str:
        return string[::-1]


@bot.tree.command(name="reverse")
async def reverse(interaction: Interaction, to_reverse: Transform[str, Reverser]):
    await interaction.response.send_message(to_reverse)
    
    
class GreeterButton(Button):
    
    def __init__(self):
        super().__init__()
        self.label = "Greet"
        
    async def callback(self, interaction: Interaction):
        await interaction.response.send_message("Hello there!", ephemeral=True)
    
    
class GreeterButtonView(View):
    
    def __init__(self):
        super().__init__()
        self.add_item(GreeterButton())
    
    
@bot.tree.command(name="button")
async def button(interaction: Interaction):
    await interaction.response.send_message("Test button:", view=GreeterButtonView())


class NumberButton(Button):

    def __init__(self, number: int):
        super().__init__()
        self.label = f"{number}"
        self._number = number

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"Button {self._number} clicked", ephemeral=True)

class NumberButtonView(View):

    def __init__(self, button_count: int):
        super().__init__()
        for number in range(1, button_count + 1):
            self.add_item(NumberButton(number))
    
    
@bot.tree.command(name="buttons")
async def buttons(interaction: Interaction, count: int = 2):
    await interaction.response.send_message("Click numbers:", view=NumberButtonView(count)) 
    
    
class ExampleModal(Modal, title="Example modal"):

    def __init__(self, raw_response: bool = False):
        super().__init__()
        self._raw_response = raw_response

    response = TextInput(label="Say something", placeholder="text")

    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(self.response if self._raw_response else self.response.value)
    
    
@bot.tree.command(name="modal")
async def modal(interaction: Interaction, raw_response: bool = False):
    await interaction.response.send_modal(ExampleModal(raw_response))


if __name__ == '__main__':
    bot.run(_get_secret("TOKEN"))
