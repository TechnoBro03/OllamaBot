import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional, Tuple
from pathlib import Path

@dataclass(slots=True)
class GuildSettings:
	"""
	A data class for guild-specific settings.

	Attributes:
		guild_id (int): The ID of the guild this configuration belongs to.
		system_prompt (str): The system prompt to use for the guild.
		model (str): The Ollama model to use for the guild.
		required_role (Optional[int]): The ID of the role required to use the bot in this guild, or None if no role is required.
		reply_history (int): The number of messages to include in the reply history for the bot.
		message_history (int): The number of messages to include in the message history for the bot.
		on_change (Optional[Callable[[], None]]): A callback function that is called whenever a setting is changed.
	"""

	guild_id: int
	"""
	The ID of the guild this configuration belongs to.
	"""

	system_prompt: str = field(default="You are a helpful assistant.")
	"""
	The system prompt to use for the guild.
	"""

	model: str = field(default="llama3")
	"""
	The Ollama model to use for the guild.
	"""

	required_role: Optional[int] = field(default=None)
	"""
	The ID of the role required to use the bot in this guild, or None if no role is required.
	"""

	reply_history: int = field(default=10)
	"""
	The number of messages to include in the reply history for the bot.
	"""

	message_history: int = field(default=10)
	"""
	The number of messages to include in the message history for the bot.
	"""

	on_change: Optional[Callable[[], None]] = field(default=None, repr=False, compare=False)
	"""
	A callback function that is called whenever a setting is changed.
	"""

	def __setattr__(self, key: str, value: Any):
		"""
		Sets an attribute and calls the on_change callback if it exists.

		Args:
			key (str): The name of the attribute to set.
			value (Any): The value to set the attribute to.
		"""
		object.__setattr__(self, key, value)
		if key != "on_change" and callable(callback := getattr(self, "on_change", None)):
			callback()

	@staticmethod
	def dict_factory(items: Iterable[Tuple[str, Any]]) -> Dict[str, Any]:
		"""
		Custom dictionary factory to exclude certain keys from the serialized output.
		
		Args:
			items (Iterable[Tuple[str, Any]]): An iterable of key-value pairs to convert to a dictionary.
		"""
		excluded = ("on_change",)
		return {k: v for (k, v) in items if ((v is not None) and (k not in excluded))}

class SettingsManager:
	"""
	A manager for guild settings.

	This will automatically load and save settings to a JSON file.

	Attributes:
		guild_settings (Dict[int, GuildSettings]): A dictionary mapping guild IDs to their settings.
		path (str): The path to the JSON file where guild settings are stored.
	"""

	def __init__(self, path: str):
		""""
		Initializes the SettingsManager and loads guild settings from a file.

		Args:
			path (str): The path to the JSON file where guild settings are stored.
		"""
		self.path = path
		self.guild_settings: Dict[int, GuildSettings] = {}
		self.load()

	def __getitem__(self, key: int) -> GuildSettings:
		"""
		Gets the guild settings for a specific guild ID, creating a new instance if it doesn't exist.

		Args:
			key (int): The ID of the guild whose settings are being accessed.
		"""
		if key not in self.guild_settings:
			self.guild_settings[key] = GuildSettings(
				guild_id=key,
				on_change=lambda: self.save()
			)

		return self.guild_settings[key]
	
	def __setitem__(self, key: int, value: GuildSettings):
		"""
		Sets the guild settings for a specific guild ID.

		Args:
			key (int): The ID of the guild whose settings are being set.
			value (GuildSettings): The new settings for the guild.
		"""
		self.guild_settings[key] = value

	def load(self):
		"""
		Loads guild settings from a JSON file.
		"""
		if not Path(self.path).exists():
			logging.getLogger("discord.OllamaBot.GuildConfigManager").error(f"File not found: {self.path}.")
			return

		try:
			with open(self.path, "r", encoding="utf-8") as f:
				data = json.load(f)

			for gid_str, data in data.items():
				self[int(gid_str)] = GuildSettings(
					**data,
					on_change = lambda: self.save()
				)

			logging.getLogger("discord.OllamaBot.GuildConfigManager").debug(f"Settings loaded from {self.path}.")

		except Exception as e:
			self.guild_settings.clear()
			logging.getLogger("discord.OllamaBot.GuildConfigManager").error(f"Error loading settings from {self.path}: {e}")
	
	def save(self):
		"""
		Saves the current guild settings to a JSON file.
		"""
		try:
			serializable = {
				gid: asdict(settings, dict_factory = GuildSettings.dict_factory)
				for gid, settings in self.guild_settings.items()
			}

			path_obj = Path(self.path)
			path_obj.parent.mkdir(parents=True, exist_ok=True)
			with open(self.path, "w") as f:
				json.dump(serializable, f, indent = 2)

			logging.getLogger("discord.OllamaBot.GuildConfigManager").debug(f"Settings saved to {self.path}.")

		except Exception as e:
			logging.getLogger("discord.OllamaBot.GuildConfigManager").error(f"Error saving settings to {self.path}: {e}")
