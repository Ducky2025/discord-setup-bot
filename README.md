# Discord Server Setup Bot

A simple Python Discord bot that automatically sets up basic roles, categories, and channels for a new server using slash commands. Ideal for quickly bootstrapping a new community server.

## Features

*   Creates standard roles (Admin, Moderator, Member, Muted, Bot) with basic permissions.
*   Sets up organized channel categories (Info, General, Voice, Staff).
*   Creates essential channels within categories (`#welcome`, `#rules`, `#general-chat`, `General` voice, etc.).
*   Configures basic permissions for roles and channels (e.g., makes Info channels read-only, Staff category private).
*   Uses an easy-to-use slash command (`/setup_beginner`).
*   Keeps your sensitive Bot Token secure using a `.env` file (not stored on GitHub).

## Prerequisites

Before you begin, ensure you have the following installed or set up:

1.  **Python:** Version 3.8 or higher recommended.
2.  **pip:** Python's package installer (usually comes with Python).
3.  **Git:** For cloning the repository.
4.  **Discord Bot Token:** You need to create a Bot Application on the [Discord Developer Portal](https://discord.com/developers/applications) and get its token.
    *   Make sure to enable **Privileged Gateway Intents** (Server Members Intent and Message Content Intent are often useful, though this bot primarily uses slash commands) on your Bot's page in the Developer Portal.
5.  **A Text Editor:** To create and edit the `.env` file (e.g., Nano in terminal, Acode on Android, VS Code on desktop).

## Installation Steps

1.  **Clone the Repository:**
    Open your terminal or command prompt and run:
    ```bash
     https://github.com/Ducky2025/discord-setup-bot
      ```

2.  **Navigate to the Directory:**
    Change into the newly downloaded folder:
    ```bash
    cd discord-setup-bot
    ```

3.  **Install Dependencies:**
    Install the required Python libraries using pip and the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    *(If `pip` doesn't work, try `pip3`)*

## Configuration (Setting Up Your Bot Token)

This bot uses a `.env` file to securely store your Bot Token without adding it to version control.

1.  **Create the `.env` file:**
    In the main project directory (the *same folder* where `setup_bot.py` is located), create a new file named exactly:
    ```
    .env
    ```
    *(Note the dot `.` at the beginning)*

2.  **Add Your Token:**
    Open the `.env` file with your text editor and add the following line, replacing `"YOUR_ACTUAL_BOT_TOKEN_HERE"` with your **real Bot Token** obtained from the Discord Developer Portal:
    ```env
    DISCORD_BOT_TOKEN="YOUR_ACTUAL_BOT_TOKEN_HERE"
    ```
    *   **IMPORTANT:** Keep the double quotes `""` around your token.
    *   **DO NOT** share this `.env` file or commit it to Git. The included `.gitignore` file should prevent accidental uploads.

## Running the Bot

1.  **Navigate (if needed):** Make sure your terminal is still in the project directory (`discord-setup-bot`).
2.  **Run the Script:** Execute the Python script using:
    ```bash
    python setup_bot.py
    ```
    *(If `python` doesn't work, try `python3`)*

3.  **Keep it Running:** The terminal window where you ran the command must stay open for the bot to remain online. If you see output like `Logged in as YourBotName...` and no errors, the bot is running!

## Usage in Discord

1.  **Invite the Bot:** You need to invite the bot to your Discord server.
    *   Go to your Bot Application page on the [Discord Developer Portal](https://discord.com/developers/applications).
    *   Navigate to "OAuth2" -> "URL Generator".
    *   Select the scopes: `bot` and `applications.commands`.
    *   Select Bot Permissions: **Administrator** (this is required for the bot to create roles and channels correctly).
    *   Copy the generated URL and paste it into your browser. Select your server and authorize the bot.

2.  **Run the Setup Command:**
    *   Go to any text channel in the Discord server where you invited the bot.
    *   Make sure you have **Administrator** permissions in that Discord server yourself.
    *   Type `/` and select the `setup_beginner` command from the list that appears, or type `/setup_beginner` fully.
    *   Press Enter.
    *   The bot will respond with ephemeral messages (only visible to you) showing the setup progress and a final confirmation. Check your server's channels and roles!
