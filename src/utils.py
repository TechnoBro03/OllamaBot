import asyncio
from ollama import Image, Message as OllamaMessage
from discord import MessageType, Message as DiscordMessage, Interaction, Member
from discord.app_commands import CheckFailure
from typing import TYPE_CHECKING, AsyncIterator, cast

if TYPE_CHECKING:
	from ollama_bot import OllamaBot

def has_required_role(interaction: Interaction) -> bool:
	"""
	Checks if the user has the required role to execute a command.

	Args:
		interaction (Interaction): The interaction that triggered the command.

	Returns:
		bool: True if the user has the required role, False otherwise.

	Raises:
		CheckFailure: If an error occurs while checking the role or if the user is not a member of a guild.
	"""
	if interaction.guild is None or not isinstance(interaction.user, Member):
		raise ValueError("Guild is not defined or user is not a member.")

	client: "OllamaBot" = cast("OllamaBot", interaction.client)

	config = client.settings_manager[interaction.guild.id]
	
	if config.required_role is None or config.required_role in [role.id for role in interaction.user.roles]:
		return True

	raise CheckFailure(f"You don't have permission to use this command.")

async def reply_history(message: DiscordMessage, limit: int = 100) -> AsyncIterator[DiscordMessage]:
	"""
	Iteratively retrieves the history of messages that this message is replying to, starting after this message.

	Args:
		message (Message): The message to start after.
		limit (int): The maximum number of messages to retrieve in the history.

	Yields:
		Message: Messages in the reply history, starting after this message.
	"""
	count = 0
	current_message = message

	while True:
		if count >= limit:
			break

		if current_message.type != MessageType.reply:
			break

		if not current_message.reference or not current_message.reference.message_id:
			break

		try:
			resolved_message = current_message.reference.resolved or await current_message.channel.fetch_message(current_message.reference.message_id)
		except:
			break

		if not isinstance(resolved_message, DiscordMessage):
			break

		yield resolved_message
		current_message = resolved_message
		count += 1

async def to_ollama_message(discord_client: "OllamaBot", message: DiscordMessage) -> OllamaMessage:
	"""
	Converts a Discord message to an Ollama message.

	Args:
		discord_client (OllamaBot): The Ollama bot client instance.
		message (Message): The Discord message to convert.

	Returns:
		OllamaMessage: The converted Ollama message.
	"""
	if message.author == discord_client.user:
		role = "assistant"
		content = f"{message.content}"
	else:
		role = "user"
		content = f"{message.author.mention}: {message.content}"

	# Remove mentions of the bot (they can confuse the model)
	if discord_client.user:
		content = content.replace(discord_client.user.mention, "")

	# Get images from attachments
	image_attachments = [attachment for attachment in message.attachments if attachment.content_type and attachment.content_type.startswith("image/")]
	image_data = await asyncio.gather(*(attachment.read() for attachment in image_attachments))
	images = [Image(value=image) for image in image_data]

	return OllamaMessage(role=role, content=content, images=images)
