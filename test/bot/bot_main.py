import json
import os

from discord import Client, Intents, Object, Interaction
from discord.app_commands import CommandTree, Transform, Transformer


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


@bot.tree.command(name="repeat")
async def repeat(interaction: Interaction, to_repeat: str, times: int = 2):
    await interaction.response.send_message(f"{to_repeat}\n" * times)


class Reverser(Transformer):
    async def transform(self, _: Interaction, string: str) -> str:
        return string[::-1]


@bot.tree.command(name="reverse")
async def reverse(interaction: Interaction, to_reverse: Transform[str, Reverser]):
    await interaction.response.send_message(to_reverse)


if __name__ == '__main__':
    bot.run(_get_secret("TOKEN"))
