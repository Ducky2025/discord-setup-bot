import discord
from discord import app_commands # Required for slash commands
from discord.ext import commands
import os
import asyncio # For potential delays to avoid rate limits

# --- Configuration ---
# It's best practice to use environment variables for your token!
# You can set this in your system or use a .env file with python-dotenv library
# For testing, you can temporarily hardcode it, BUT DON'T SHARE IT or commit it!
# BOT_TOKEN = "YOUR_SUPER_SECRET_BOT_TOKEN"
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") # Recommended way

if not BOT_TOKEN:
    print("ERROR: DISCORD_BOT_TOKEN environment variable not set.")
    exit()

# --- Bot Setup ---
# Define necessary intents. Guilds are needed for basic info.
# Administrator permission implicitly grants many intents, but specifying is good practice.
intents = discord.Intents.default()
intents.guilds = True # Needed to see guilds the bot is in
# intents.members = True # Might be needed for specific role assignments later

# Use commands.Bot for potential prefix commands later, or just discord.Client if only slash commands
bot = commands.Bot(command_prefix="!", intents=intents) # Prefix is fallback, we focus on slash commands

# --- Define Server Structure ---
# Structure: {'Category Name': ['#channel-name', '#another-channel']}
# Use None for category if channels should not be under one.
SERVER_STRUCTURE = {
    "▬▬▬ INFO ▬▬▬": [
        "welcome",
        "rules",
        "announcements",
        "roles-info", # Optional place for reaction roles later
    ],
    "▬▬▬ GENERAL ▬▬▬": [
        "general-chat",
        "media",
        "bot-commands",
    ],
    "▬▬▬ VOICE ▬▬▬": [
        "General", # Voice channels don't use '#'
        "Music",
        "AFK",
    ],
    "▬▬▬ STAFF AREA ▬▬▬": [ # This category will be private
        "mod-chat",
        "mod-logs",
    ]
}

# Define roles to create
ROLES_TO_CREATE = [
    {"name": "Admin", "permissions": discord.Permissions(administrator=True), "colour": discord.Colour.red()},
    {"name": "Moderator", "permissions": discord.Permissions(manage_channels=True, manage_roles=True, kick_members=True, ban_members=True, manage_messages=True, mute_members=True, deafen_members=True, move_members=True), "colour": discord.Colour.blue()},
    {"name": "Member", "permissions": discord.Permissions.general(), "colour": discord.Colour.green()}, # Start with basic perms
    {"name": "Muted", "permissions": discord.Permissions.none(), "colour": discord.Colour.dark_grey()}, # Will deny sending msgs via overwrites
    {"name": "Bot", "permissions": discord.Permissions.none(), "colour": discord.Colour.purple()} # For organizing bots
]


# --- Event: Bot Ready ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    try:
        # Sync slash commands with Discord. Important!
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# --- Slash Command: Setup Beginner ---
# Use @bot.tree.command for slash commands
@bot.tree.command(name="setup_beginner", description="Automatically sets up basic roles and channels for a new server.")
@app_commands.checks.has_permissions(administrator=True) # IMPORTANT: Only admins can run this
async def setup_beginner(interaction: discord.Interaction):
    """Sets up the server with predefined roles, categories, and channels."""

    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    # Defer the response immediately, as setup can take time
    await interaction.response.defer(ephemeral=True, thinking=True) # Ephemeral=True so only user sees progress

    print(f"Setup command initiated by {interaction.user} in server {guild.name}")
    log_messages = ["Starting server setup...\n"]

    created_roles = {} # Store created role objects {name: role_object}
    permission_errors = []

    # == 1. Create Roles ==
    log_messages.append("**Creating Roles:**")
    for role_info in ROLES_TO_CREATE:
        role_name = role_info["name"]
        existing_role = discord.utils.get(guild.roles, name=role_name)
        if existing_role:
            log_messages.append(f"- Role '{role_name}' already exists. Skipping.")
            created_roles[role_name] = existing_role # Store existing role too
            continue
        try:
            new_role = await guild.create_role(
                name=role_name,
                permissions=role_info["permissions"],
                colour=role_info["colour"],
                reason=f"Setup by {bot.user.name}"
            )
            log_messages.append(f"- Created role: {new_role.mention}")
            created_roles[role_name] = new_role
            await asyncio.sleep(0.5) # Small delay to help avoid rate limits
        except discord.Forbidden:
            log_messages.append(f"- **ERROR:** Missing permissions to create role '{role_name}'.")
            permission_errors.append(f"create role '{role_name}'")
        except Exception as e:
            log_messages.append(f"- **ERROR:** Failed to create role '{role_name}': {e}")

    # Fetch roles needed for permission setting
    admin_role = created_roles.get("Admin")
    mod_role = created_roles.get("Moderator")
    member_role = created_roles.get("Member")
    muted_role = created_roles.get("Muted")
    everyone_role = guild.default_role # This is @everyone

    # == 2. Create Categories and Channels ==
    log_messages.append("\n**Creating Categories & Channels:**")
    for category_name, channels in SERVER_STRUCTURE.items():
        existing_category = discord.utils.get(guild.categories, name=category_name)
        category_obj = None
        if existing_category:
            log_messages.append(f"- Category '{category_name}' already exists. Using existing.")
            category_obj = existing_category
        else:
            try:
                # --- Define Category Permissions ---
                category_overwrites = {
                    everyone_role: discord.PermissionOverwrite(read_messages=False, connect=False), # Deny by default
                    member_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True), # Base perms for members
                    mod_role: discord.PermissionOverwrite(manage_channels=True, manage_messages=True, read_messages=True, connect=True, speak=True, priority_speaker=True, move_members=True), # Mod permissions
                    admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True), # Admins inherit via role perm, but explicit good too
                    muted_role: discord.PermissionOverwrite(send_messages=False, add_reactions=False, speak=False, stream=False) # Mute override
                }

                # --- Adjust Specific Category Permissions ---
                if category_name == "▬▬▬ INFO ▬▬▬":
                     category_overwrites[everyone_role].update(read_messages=True) # Everyone can see info
                     category_overwrites[member_role].update(send_messages=False, connect=False, speak=False) # Read-only for members

                if category_name == "▬▬▬ STAFF AREA ▬▬▬":
                    category_overwrites[member_role].update(read_messages=False, connect=False) # Hide from members
                    category_overwrites[everyone_role].update(read_messages=False) # Hide from everyone else too
                    # Admins/Mods already have access from base overwrite

                category_obj = await guild.create_category(
                    category_name,
                    overwrites=category_overwrites,
                    reason=f"Setup by {bot.user.name}"
                )
                log_messages.append(f"- Created category: {category_obj.name}")
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                log_messages.append(f"- **ERROR:** Missing permissions to create category '{category_name}'.")
                permission_errors.append(f"create category '{category_name}'")
                continue # Skip channels in this category if category creation failed
            except Exception as e:
                log_messages.append(f"- **ERROR:** Failed to create category '{category_name}': {e}")
                continue

        # Create channels within the category
        for channel_name in channels:
            is_voice = not channel_name.startswith("#")
            clean_channel_name = channel_name.lstrip("#") # Remove '#' for text channel creation name
            existing_channel = discord.utils.get(guild.channels, name=clean_channel_name, category=category_obj)

            if existing_channel:
                log_messages.append(f"  - Channel '{clean_channel_name}' already exists. Skipping.")
                continue
            try:
                if is_voice:
                    # Voice channel permissions usually inherited from category are fine
                    new_channel = await guild.create_voice_channel(
                        clean_channel_name,
                        category=category_obj,
                        reason=f"Setup by {bot.user.name}"
                    )
                    # Specific AFK channel setting needs manual server config
                    if clean_channel_name.lower() == "afk":
                         log_messages.append(f"  - Created voice channel: {new_channel.name} (Set as AFK channel in Server Settings -> Overview)")
                    else:
                        log_messages.append(f"  - Created voice channel: {new_channel.name}")

                else: # It's a text channel
                    # Text channel permissions usually inherited from category are fine
                     # Example override: Make #rules read-only even if category allows sending for Member
                    channel_overwrites = {}
                    if clean_channel_name in ["rules", "announcements", "roles-info", "welcome"]:
                        # Ensure read-only for members in these specific channels
                         if member_role:
                             channel_overwrites[member_role] = discord.PermissionOverwrite(send_messages=False, add_reactions=False) # Deny sending
                         if everyone_role: # Also deny @everyone sending if they somehow got perms
                             channel_overwrites[everyone_role] = discord.PermissionOverwrite(send_messages=False, add_reactions=False)

                    new_channel = await guild.create_text_channel(
                        clean_channel_name,
                        category=category_obj,
                        overwrites=channel_overwrites, # Apply specific overrides if any
                        reason=f"Setup by {bot.user.name}"
                    )
                    log_messages.append(f"  - Created text channel: {new_channel.mention}")
                await asyncio.sleep(0.5) # Small delay
            except discord.Forbidden:
                log_messages.append(f"  - **ERROR:** Missing permissions to create channel '{clean_channel_name}'.")
                permission_errors.append(f"create channel '{clean_channel_name}'")
            except Exception as e:
                log_messages.append(f"  - **ERROR:** Failed to create channel '{clean_channel_name}': {e}")

    # == 3. Final Report ==
    log_messages.append("\n**Setup Complete!**")
    if permission_errors:
        log_messages.append("\n**Permissions Errors Encountered:**")
        log_messages.append("The bot might be missing necessary permissions for:")
        for item in permission_errors:
            log_messages.append(f"- {item}")
        log_messages.append("\nPlease check the bot's role permissions and try again if needed.")

    log_messages.append("\n**Recommended Next Steps:**")
    log_messages.append("- Configure Server Settings (Icon, Name, Region, Verification Level, AFK Channel).")
    log_messages.append("- Review and customize the created #rules channel.")
    log_messages.append("- Assign the 'Admin' and 'Moderator' roles to trusted users.")
    log_messages.append("- Consider adding other bots (e.g., moderation logging, music).")

    # Send the final report as a follow-up message (since we deferred)
    # Discord messages have a character limit (2000), split if necessary
    full_log = "\n".join(log_messages)
    if len(full_log) > 1950: # Leave some buffer
         parts = [full_log[i:i + 1950] for i in range(0, len(full_log), 1950)]
         for part in parts:
             await interaction.followup.send(f"```\n{part}\n```", ephemeral=True)
    else:
        await interaction.followup.send(f"```\n{full_log}\n```", ephemeral=True)


# --- Error Handler for Permissions ---
@setup_beginner.error
async def setup_beginner_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You must be an Administrator to use this command.", ephemeral=True)
    else:
        print(f"An error occurred in setup_beginner command: {error}")
        await interaction.response.send_message("❌ An unexpected error occurred. Please check the bot's console.", ephemeral=True)


# --- Run the Bot ---
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
