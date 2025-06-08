import asyncio
import os
import signal
import logging
from dotenv import load_dotenv
from ollama_bot import OllamaBot
from ollama import AsyncClient
from discord import Intents

# Configure root logger
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("discord.OllamaBot")

async def main():
	"""
	Main function to run the Ollama Discord bot.
	"""
	# Load environment variables from .env file
	load_dotenv()

	# Get environment variables
	DISCORD_APP_TOKEN = os.getenv("DISCORD_APP_TOKEN", None)
	OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", None)

	# Ensure required environment variables are set
	if not DISCORD_APP_TOKEN or not OLLAMA_API_URL:
		raise ValueError("Environment variables must be set.")

	# Graceful shutdown handler
	shutdown_event = asyncio.Event()

	# Register signal handlers (note: SIGTERM won't work on Windows)
	loop = asyncio.get_running_loop()
	for sig in (signal.SIGINT, signal.SIGTERM):
		try:
			loop.add_signal_handler(sig, lambda: {
				logger.info(f"Received signal {sig.name}"),
				shutdown_event.set()
			})
		except NotImplementedError:
			pass # Windows + SIGTERM

	try:
		# Initialize the Ollama client
		ollama_client = AsyncClient(OLLAMA_API_URL)

		# Set intents for the Discord client
		intents = Intents.default()
		intents.message_content = True
		intents.guilds = True

		discord_client = OllamaBot(intents=intents, ollama_client=ollama_client)

		task: asyncio.Task | None = None

		try:
			# Start the Discord client
			task = asyncio.create_task(discord_client.start(DISCORD_APP_TOKEN))

			# Wait for shutdown event
			await shutdown_event.wait()
		except Exception as e:
			logger.error(f"Error during bot operation: {e}")
		finally:
			# Gracefully shutdown the bot
			logger.info("Shutting down the bot...")

			await discord_client.close()
			if task:
				await task

	except Exception as e:
		logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logger.info("KeyboardInterrupt received.")
	except Exception as e:
		logger.error(f"Unhandled exception: {e}")
	finally:
		logger.info("Exiting...")
