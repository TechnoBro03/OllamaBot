import time
from discord import app_commands, Interaction
from discord.app_commands import Choice
from typing import TYPE_CHECKING, cast, List
from utils import has_required_role

if TYPE_CHECKING:
	from ollama_bot import OllamaBot

_model_cache: tuple[float, List[Choice]] = (0.0, [])
"""
A cache for Ollama models to avoid frequent API calls.

(float: The last fetch time, List[Choice]: A list of Choices representing the available models )
"""

async def model_autocomplete(interaction: Interaction, current: str):
	"""
	Autocomplete function for Ollama models.

	Args:
		interaction (Interaction): The interaction that triggered the autocomplete.
		current (str): The current input string for the autocomplete.
	"""
	global _model_cache

	client = cast("OllamaBot", interaction.client)
	ollama_client = client.ollama_client

	now = time.monotonic()
	last_fetch_time, cached_models = _model_cache

	# Refresh the cache if it has been more than 10 seconds since the last fetch
	if now - last_fetch_time > 10:
		try:
			models = await ollama_client.list()
			_model_cache = (now, [app_commands.Choice(name=model.model, value=model.model) for model in models.models if model.model is not None])
		except Exception as e:
			_model_cache = (now, [])
			return []
		
	return [choice for choice in cached_models if current.lower() in choice.name.lower()][:25] # Discord limits to 25 choices

@app_commands.guild_only()
class ModelGroup(app_commands.Group):
	def __init__(self):
		"""
		Initializes the ModelGroup for managing models in a Discord guild.
		"""
		super().__init__(name="model", description="Manage Ollama model settings.")

	@app_commands.command(name="set", description="Set the model for this guild.")
	@app_commands.describe(model="The Ollama model to set for this guild.")
	@app_commands.autocomplete(model=model_autocomplete)
	@app_commands.check(has_required_role)
	async def set(self, interaction: Interaction, model: str):
		"""
		Sets the model to use for the guild.

		Args:
			interaction (Interaction): The interaction that triggered the command.
			model (str): The model to set for the guild.

		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")
		
		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		config = client.settings_manager[interaction.guild.id]
		config.model = model

		await interaction.response.send_message(f"Model set for this guild.", ephemeral=True)

	@app_commands.command(name="get", description="Get the current model for this guild.")
	@app_commands.check(has_required_role)
	async def get(self, interaction: Interaction):
		"""
		Gets the current model for the guild.

		Args:
			interaction (Interaction): The interaction that triggered the command.
		
		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")

		client: "OllamaBot" = cast("OllamaBot", interaction.client)
		config = client.settings_manager[interaction.guild.id]

		await interaction.response.send_message(f"Current model for this guild: `{config.model}`", ephemeral=True)
		
	@app_commands.command(name="list", description="List all available models.")
	@app_commands.check(has_required_role)
	async def list(self, interaction: Interaction):
		"""
		Lists the available models.

		Args:
			interaction (Interaction): The interaction that triggered the command.
		"""
		await interaction.response.defer(ephemeral=True)

		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		try:
			response = await client.ollama_client.list()
		except Exception as e:
			await interaction.followup.send(f"Failed to retrieve models: {e}", ephemeral=True)
			return

		formatted_models = "\n- ".join([f"`{model.model}` ({(model.size.real / 1024 / 1024 / 1024 if model.size else 0):.2f} GB)" for model in response.models])
		response_text = f"Available models:\n- {formatted_models}" if formatted_models else "No models available. Use '/settings model pull' to add a model."

		await interaction.followup.send(response_text, ephemeral=True)

	@app_commands.command(name="pull", description="Pull a model from Ollama. This may take a while...")
	@app_commands.describe(model="The model to pull.")
	@app_commands.check(has_required_role)
	async def pull(self, interaction: Interaction, model: str):
		"""
		Pulls a model from Ollama.

		Args:
			interaction (Interaction): The interaction that triggered the command.
			model (str): The model to pull.
		"""
		await interaction.response.defer(ephemeral=True)

		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		try:
			await client.ollama_client.pull(model)
			await interaction.followup.send(f"Model pulled successfully.", ephemeral=True)
		except Exception as e:
			await interaction.followup.send(f"Failed to pull model: {e}", ephemeral=True)
