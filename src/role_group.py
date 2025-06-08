from discord import Role, app_commands, Interaction
from typing import cast, TYPE_CHECKING
from utils import has_required_role

if TYPE_CHECKING:
	from ollama_bot import OllamaBot

@app_commands.guild_only()
class RoleGroup(app_commands.Group):
	"""
	A group of commands for managing the required role in a Discord guild.
	"""
	def __init__(self):
		"""
		Initializes the RoleGroup for managing the required role in a Discord guild.
		"""
		super().__init__(name="role", description="Manage the configuration role.")

	@app_commands.command(name="set", description="Set the required role for this guild.")
	@app_commands.describe(role="The required role to set for this guild. Leaving this blank will clear the required role.")
	@app_commands.check(has_required_role)
	async def set(self, interaction: Interaction, role: Role | None = None):
		"""
		Sets the required role for the guild.

		Args:
			interaction (Interaction): The interaction that triggered the command.
			role (Role | None): The role to set as the required role for the guild. If None, clears the required role.

		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")

		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		config = client.settings_manager[interaction.guild.id]
		config.required_role = role.id if role else None

		await interaction.response.send_message(f"Required role set for this guild.", ephemeral=True)

	@app_commands.command(name="get", description="Get the required role for this guild.")
	@app_commands.check(has_required_role)
	async def get(self, interaction: Interaction):
		"""
		Gets the current required role for the guild.

		Args:
			interaction (Interaction): The interaction that triggered the command.

		Raises:
			ValueError: If the guild is not defined in the interaction.
		"""
		if interaction.guild is None:
			raise ValueError("Guild is not defined.")

		client: "OllamaBot" = cast("OllamaBot", interaction.client)

		config = client.settings_manager[interaction.guild.id]

		if config.required_role and (role := interaction.guild.get_role(config.required_role)):
			await interaction.response.send_message(f"Current required role for this guild: {role.mention}", ephemeral=True)
			return

		await interaction.response.send_message("No required role is currently set.", ephemeral=True)
