from discord import app_commands
from model_group import ModelGroup
from prompt_group import PromptGroup
from role_group import RoleGroup
from history_group import HistoryGroup

class SettingsGroup(app_commands.Group):
	"""
	A group of commands for managing guild settings in a Discord bot.
	"""
	def __init__(self):
		super().__init__(name="settings", description="Manage guild settings.")

		# Add subgroups
		self.add_command(ModelGroup())
		self.add_command(PromptGroup())
		self.add_command(RoleGroup())
		self.add_command(HistoryGroup())