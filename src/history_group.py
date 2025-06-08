from discord import app_commands, Interaction
from typing import TYPE_CHECKING, cast
from utils import has_required_role

if TYPE_CHECKING:
	from ollama_bot import OllamaBot

@app_commands.guild_only()
class HistoryGroup(app_commands.Group):
	"""
	A group of commands for managing the message history settings in a Discord guild.
	"""
	def __init__(self):
		"""
		Initializes the HistoryGroup for managing history settings in a Discord guild.
		"""
		super().__init__(name="history", description="Manage the message history settings.")

	@app_commands.command(name="set", description="Set message history settings for this guild.")
	@app_commands.describe(reply_history="Number of messages to include in the reply history", message_history="Number of messages to include in the message history")
	@app_commands.check(has_required_role)
	async def set(self, interaction: Interaction, reply_history: int = 10, message_history: int = 10):
		"""
		Sets the message history settings for the guild.

		Args:
			interaction (Interaction): The interaction that triggered the command.
			reply_history (int): The number of messages to include in the reply history.
			message_history (int): The number of messages to include in the message history.

		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")
		
		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		config = client.settings_manager[interaction.guild.id]
		config.reply_history = reply_history
		config.message_history = message_history

		await interaction.response.send_message(f"Message history set for this guild.", ephemeral=True)

	@app_commands.command(name="get", description="Get the current message history settings for this guild.")
	@app_commands.check(has_required_role)
	async def get(self, interaction: Interaction):
		"""
		Gets the current message history settings for the guild.

		Args:
			interaction (Interaction): The interaction that triggered the command.

		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")
		
		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		config = client.settings_manager[interaction.guild.id]

		await interaction.response.send_message(
			f"Message history settings for this guild:\n"
			f"- Reply History: `{config.reply_history}`\n"
			f"- Message History: `{config.message_history}`",
			ephemeral=True
		)
