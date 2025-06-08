import asyncio
from io import BytesIO
import logging
from ollama import AsyncClient, Message as OllamaMessage
from discord import Client, File, Intents, Message as DiscordMessage, Interaction
from discord.app_commands import CommandTree, CheckFailure, AppCommandError
from settings_manager import SettingsManager
from settings_group import SettingsGroup
from utils import to_ollama_message, reply_history

SYSTEM_PROMPT = "\
You are in a discord server. \
Every user message is prefixed with their username, colon and space '<@USERID>: ' this is metadata. \
When referring to a user, use their username '<@USERID>'. Example: 'Hello <@123456789012345678>!'."

MAX_LENGTH = 2000 # Maximum length for a Discord message reply

class OllamaBot(Client):
	"""
	A Discord client that integrates with the Ollama API to generate responses based on user messages.
	
	Attributes:
		intents (Intents): The intents for the Discord client.
		ollama_client (AsyncClient): The Ollama API client for generating responses.
		settings_manager (SettingsManager): Manages guild settings.
		tree (CommandTree): The command tree for the bot, used to register commands and interactions.
	"""
	def __init__(self, *, intents: Intents = Intents.default(), ollama_client: AsyncClient, **options):
		super().__init__(intents=intents, **options)

		# Set up the internal variables
		self.logger = logging.getLogger("discord.OllamaBot")
		self.settings_manager = SettingsManager("./data/settings.json")

		self.ollama_client = ollama_client

		# Initialize the command tree
		self.tree = CommandTree(self)
		self.tree.error(self.on_app_command_error)

		# Register events
		self.event(self.on_ready)
		self.event(self.on_message)

		# Register commands
		self.tree.add_command(SettingsGroup())

	# --- Client Overrides ---
	async def setup_hook(self):
		await self.tree.sync()
		self.logger.info(f'Synced commands: {[command.name for command in self.tree.get_commands()]}')

	# --- Discord Client Events ---
	async def on_ready(self):
		"""
		Event called when the client is logged in and ready to receive events.
		"""
		self.logger.info(f"Logged in as {self.user}")

	async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
		"""
		Event called when an application command (slash command) encounters an error.

		Args:
			interaction (Interaction): The interaction that triggered the command.
			error (AppCommandError): The error that occurred during command execution.
		"""
		self.logger.error(f"Command error: {error}")

		if interaction.response.is_done():
			return

		try:
			if isinstance(error, CheckFailure):
				await interaction.response.send_message(
					"You don't have permission to use this command.",
					ephemeral=True
				)
			else:
				await interaction.response.send_message(
					f"An unexpected error occurred: {error}",
					ephemeral=True
				)
		except Exception as e:
			self.logger.error(f"Failed to send error response: {e}")

	async def on_message(self, message: DiscordMessage):
		"""
		Event called when a message is received.

		Args:
			message (Message): The message that was received.
		"""
		try:
			# Ignore messages from itself to prevent loops
			if message.author == self.user:
				return

			# Directly mentioning the bot (@bot) AND replying to the bot inject the bot's user into 'message.mentions'.
			# Ignore messages that do not mention the bot
			if self.user not in message.mentions:
				return

			# Signal that the bot is typing in the channel
			async with message.channel.typing():
				if message.guild is None:
					self.logger.warning("Guild is not defined, ignoring message.")
					return

				config = self.settings_manager[message.guild.id]

				# Get the previous messages in the channel, including replies (if any)
				message_history = [message async for message in message.channel.history(limit=config.message_history, before=message)]
				message_replies = [reply async for reply in reply_history(message, limit=config.reply_history)]

				# Combine the message history and replies, ensuring the original message is included
				message_history = message_replies + message_history + [message]

				# Filter out non-distinct messages
				message_history = list({msg.id: msg for msg in message_history}.values())

				# Sort messages by their creation time
				message_history.sort(key=lambda msg: msg.created_at)

				# Convert the Discord message history to Ollama messages
				message_history = await asyncio.gather(*(to_ollama_message(self, msg) for msg in message_history))

				system_prompt = f"{SYSTEM_PROMPT}\n{config.system_prompt}"

				# Prepend the system prompt
				message_history.insert(0, OllamaMessage(role="system", content=system_prompt))

				# Send to the model
				try:
					response_text = (await self.ollama_client.chat(model=config.model, messages=message_history, stream=False)).message.content
				except Exception as e:
					response_text = f"Error generating response: {e}"
					self.logger.error(f"Error generating response: {e}")

				# Respond to the original message
				try:
					if response_text:
						if len(response_text) <= MAX_LENGTH:
							await message.reply(response_text)
						else:
							fp = BytesIO(response_text.encode("utf-8"))
							await message.reply("Response was too long, uploaded as file:", file=File(fp, filename="response.txt"))
					else:
						await message.reply("No response generated.")
				except Exception as e:
					self.logger.error(f"Failed to send reply: {e}")
		except Exception as e:
			self.logger.error(f"An error occurred while processing a message: {e}")
