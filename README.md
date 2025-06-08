# Ollama Bot

# Table of Contents
- [Ollama Bot](#ollama-bot)
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Usage](#usage)
    - [Commands](#commands)
    - [Bot Interaction](#bot-interaction)
- [Installation](#installation)
- [File Structure](#file-structure)
- [Local Development](#local-development)
    - [Running the Bot](#running-the-bot)
    - [Running with Docker](#running-with-docker)

# Introduction

A Discord bot that integrates with [Ollama](https://hub.docker.com/r/ollama/ollama) to generate AI-powered replies.

This bot allows you to interact with Ollama's models directly from Discord, making it easy to generate text responses, summaries, and more.\
Both the Discord bot and Ollama are designed to be run locally in Docker containers, providing a self-hosted solution for AI interactions, ensuring privacy and control over your data.

# Usage

## Commands
| **Command**                                               | **Arguments**                                  | **Description**                                           |
| --------------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------- |
| `/settings model set <model>`                             | `model` (string)                               | Set the Ollama model for this guild.                      |
| `/settings model get`                                     | none                                           | Get the current Ollama model.                             |
| `/settings model list`                                    | none                                           | List all available models from the Ollama server.         |
| `/settings model pull <model>`                            | `model` (string)                               | Download (pull) a model into Ollama.                      |
| `/settings prompt set <prompt>`                           | `prompt` (string)                              | Set the system prompt sent at the start of each chat.     |
| `/settings prompt get`                                    | none                                           | Get the current system prompt.                            |
| `/settings role set [role]`                               | `role` (@Role) or *leave blank*                | Restrict commands to users who have this role (or clear). |
| `/settings role get`                                      | none                                           | Show the currently required role (if any).                |
| `/settings history set [reply_history] [message_history]` | `reply_history` (int), `message_history` (int) | Set how many messages to fetch as context.                |
| `/settings history get`                                   | none                                           | Show current reply & message history limits.              |

## Bot Interaction
To chat with the bot you can do one of the following:
- **Mention the bot**: Mention the bot (example: `@Ollama Bot`) followed by your message.
- **Reply to the bot**: Click on the bot's message and type your reply.

Doing either will send your message to the bot, which will then generate a response using the configured Ollama model.

# Installation
To install, run, and add the bot to your Discord server, follow these steps:
1. **Create a Discord Application**:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - In the `Bot` section:
     - Note down the `Token`, as you will need it to run the bot.
     - Under `Privileged Gateway Intents`, enable the `Message Content Intent` to allow the bot to read messages.
2. **Invite the Bot to Your Server**:
   - In the `Installation` section:
     - Under `Installation Contexts`, Select `Guild Install` only.
     - Under `Default Install Settings`, add the `applications.commands` and `bot` scopes, then the `Send Messages` and `Send Messages in Threads` permissions.
     - Finally, copy the `Discord Provided Link` and paste it into your browser to invite the bot to your server.
    [!TIP]
    For more information on creating a Discord bot, refer to the [Discord Developer Portal documentation](https://discord.com/developers/docs/intro).

3. **Run Docker Compose**
    - Ensure you have [Docker](https://www.docker.com/get-started) installed.
    - Copy the `docker-compose.yml` file from this repository to your local machine.
    - Customize the `docker-compose.yml` file if necessary, such as changing mounted volumes or ports.
    - Create a `.env` file in the root directory with your Discord bot token and Ollama API URL:
      ```env
      DISCORD_APP_TOKEN=your_discord_app_token
      OLLAMA_API_URL=your_ollama_api_url
      ```
    - Run the following command to start the bot and Ollama (detached):
      ```bash
      docker compose up -d
      ```
    [!TIP]
    For more information about the Ollama Docker image, refer to the [Ollama documentation](https://hub.docker.com/r/ollama/ollama) (GPU support is available here).

# File Structure
```
.
├── .env                     The environment variables for the bot
├── .gitignore               Files and directories to ignore in git
├── README.md                Documentation for the bot
├── Dockerfile               Dockerfile to build the bot image
├── docker-compose.yml       Example Docker Compose file
├── src/                     Source code for the bot
│   ├── main.py              Main entry point for the bot
│   ├── ollama_bot.py        Discord client and message handler
│   ├── settings_manager.py  Manages settings for the bot
│   ├── history_group.py     /settings history subcommands
│   ├── model_group.py       /settings model subcommands
│   ├── prompt_group.py      /settings prompt subcommands
│   ├── role_group.py        /settings role subcommands
│   ├── settings_group.py    /settings group command
│   ├── utils.py             Utility functions for the bot
│   └── requirements.txt     Python dependencies
```

# Local Development

## Running the Bot
[!IMPORTANT]
Ollama must be running for the bot to function properly. You can run Ollama using Docker with the following command:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

To run the bot locally, follow these steps:
1. **Clone the repository**:
    ```bash
    git clone https://github.com/TechnoBro03/OllamaBot
    cd ollamabot
    ```
2. Create & activate a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3. **Install dependencies**:
    ```bash
    pip install -r src/requirements.txt
    ```
4. **Create a `.env` file** in the root directory with the following content:
    ```env
    DISCORD_APP_TOKEN=your_discord_app_token
    OLLAMA_API_URL=your_ollama_api_url
    ```
5. **Run the bot**:
    ```bash
    python src/main.py
    ```

## Running with Docker
To run the bot using Docker, follow these steps:
1. **Ensure you have Docker installed** on your machine.
2. **Create a `.env` file** in the root directory with your Discord bot token and Ollama API URL:
    ```env
    DISCORD_APP_TOKEN=your_discord_app_token
    OLLAMA_API_URL=your_ollama_api_url
    ```
3. **Build and run the Docker container**:
    ```bash
    docker build -t ollama-bot .
    docker run -d --env-file .env --name ollama-bot ollama-bot
    ```