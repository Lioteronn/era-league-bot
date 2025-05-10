# League Bot

A Discord bot for managing League teams, players, and tournaments.

## Overview

League Bot is a Discord bot built using Python with the py-cord library. It provides commands for creating and managing teams, assigning roles, tracking players, and more. The bot uses PostgreSQL for data storage and Alembic for database migrations.

## Features

- Team management (create teams, add players, assign captains)
- Role-based permissions system
- Player verification and tracking
- Logo and team profile management
- Transaction history logging
- Database integration with SQLAlchemy ORM

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- Discord Bot Token
- Discord Developer Portal access

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/league-bot.git
   cd league-bot
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory with the following variables:

   ```
   BOT_TOKEN=your_discord_bot_token
   DATABASE_URL=postgresql://username:password@hostname:port/database_name
   LOGO_PATH=./team_logos
   SUPABASE_URL=your_supabase_url (if using Supabase)
   SUPABASE_KEY=your_supabase_key (if using Supabase)
   ```

5. **Set up the database**

   Run Alembic migrations to create the database schema:

   ```bash
   alembic upgrade head
   ```

### Bot Setup on Discord

1. Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications)
2. Add a bot to your application
3. Enable all intents (Presence, Server Members, Message Content)
4. Copy your bot token to the `.env` file
5. Use the OAuth2 URL generator to create an invite link with the following permissions:
   - Manage Roles
   - Manage Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History

## Running the Bot

Start the bot using the following command:

```bash
python bot.py
```

## Commands

### Admin Commands

- `/create-team <name> [hexcode] [logo_url]` - Create a new team with optional color and logo
- `/set-captain <team_name> <user>` - Set the captain for a team
- `/force-add-player-to-team <team_name> <user>` - Force add a player to a team

### User Commands

- `/search-team <team_name>` - Display information about a team

## Project Structure

- `bot.py` - Main bot initialization and event handling
- `config.py` - Configuration and environment variables
- `intents.py` - Discord bot intents setup
- `cogs` - Command modules
  - `cogs/team_commands.py` - Team management commands
  - `permissions/` - Permission checking utilities
- `database` - Database related modules
  - `models/` - SQLAlchemy models
  - `repository/` - Data access layer
  - `database/db.py` - Database connection setup
- `images` - Image handling utilities
- `alembic` - Database migrations

## Database Models

- `Team` - Team information
- `User` - User profile data
- `TeamMember` - Team membership records
- `Transaction` - History of team-related actions
- `Invitation` - Team invitations
- `ServerConfig` - Discord server configuration
- `Guild` - Discord guild information

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request with a description of your changes

## License

This project is licensed under the MIT License.