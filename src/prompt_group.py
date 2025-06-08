from discord import app_commands, Interaction
from typing import TYPE_CHECKING, cast
from utils import has_required_role

if TYPE_CHECKING:
	from ollama_bot import OllamaBot

@app_commands.guild_only()
class PromptGroup(app_commands.Group):
	def __init__(self):
		"""
		Initializes the PromptGroup for managing system prompts in a Discord guild.
		"""
		super().__init__(name="prompt", description="Manage the system prompt settings.")

	@app_commands.command(name="set", description="Set the system prompt for this guild.")
	@app_commands.describe(prompt="The system prompt to set for this guild")
	@app_commands.check(has_required_role)
	async def set(self, interaction: Interaction, prompt: str):
		"""
		Sets the system prompt for the guild.

		Args:
			interaction (Interaction): The interaction that triggered the command.
			prompt (str): The system prompt to set for the guild.

		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")
		
		client: "OllamaBot" = cast("OllamaBot", interaction.client)
		
		config = client.settings_manager[interaction.guild.id]
		config.system_prompt = prompt

		await interaction.response.send_message(f"System prompt set for this guild.", ephemeral=True)

	@app_commands.command(name="get", description="Get the current system prompt for this guild.")
	@app_commands.check(has_required_role)
	async def get(self, interaction: Interaction):
		"""
		Gets the current system prompt for the guild.
		
		Args:
			interaction (Interaction): The interaction that triggered the command.

		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")
		
		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		config = client.settings_manager[interaction.guild.id]

		await interaction.response.send_message(f"Current system prompt for this guild: `{config.system_prompt}`", ephemeral=True)
