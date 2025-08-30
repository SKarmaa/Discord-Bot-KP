# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import os
import discord
import random
import re
import json
from discord.ext import commands

# Enable message content intent to read message content
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable member events

bot = commands.Bot(command_prefix='!', intents=intents)


# Load data from JSON file
def load_bot_data():
    """Load bot responses and config from JSON file"""
    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ bot_data.json not found! Using fallback data...")
        # Fallback data in case JSON file is missing
        return {
            "witty_responses": {
                "hello": ["Hello there! 👋"],
                "test": ["Test successful! ✅"]
            },
            "welcome_messages": ["Welcome {user}! 🎉"],
            "bot_config": {
                "samu_user_id": 783619741289414676,
                "welcome_channel_id": 762775973816696863,
                "samu_tag_reactions": ["🙈", "😊", "👋"],
                "general_reactions": ["😂", "👍", "🤔", "😎", "🔥", "✨"],
                "write_command_user_id": 235006682583793664,
                "write_command_channel_id": 766247827528744971,
                "general_channel_id": 762775973816696863
            }
        }
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing bot_data.json: {e}")
        print("Using fallback data...")
        return load_bot_data()  # This will use the fallback


# Load bot data
BOT_DATA = load_bot_data()
WITTY_RESPONSES = BOT_DATA["witty_responses"]
WELCOME_MESSAGES = BOT_DATA["welcome_messages"]
CONFIG = BOT_DATA["bot_config"]

# Extract trigger words from responses
TRIGGER_WORDS = list(WITTY_RESPONSES.keys())

print(f"📚 Loaded {len(WITTY_RESPONSES)} trigger categories")
print(f"🎉 Loaded {len(WELCOME_MESSAGES)} welcome messages")
print(f"🔧 Config loaded: {len(CONFIG)} settings")


def reload_bot_data():
    """Reload bot data from JSON file (for live updates)"""
    global BOT_DATA, WITTY_RESPONSES, WELCOME_MESSAGES, CONFIG, TRIGGER_WORDS

    BOT_DATA = load_bot_data()
    WITTY_RESPONSES = BOT_DATA["witty_responses"]
    WELCOME_MESSAGES = BOT_DATA["welcome_messages"]
    CONFIG = BOT_DATA["bot_config"]
    TRIGGER_WORDS = list(WITTY_RESPONSES.keys())

    print(
        f"🔄 Reloaded bot data: {len(TRIGGER_WORDS)} triggers, {len(WELCOME_MESSAGES)} welcomes"
    )


def find_trigger_words(message_content):
    """Find trigger words in the message content"""
    found_words = []
    message_lower = message_content.lower()

    for word in TRIGGER_WORDS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, message_lower):
            found_words.append(word)

    return found_words


def get_witty_response(trigger_word):
    """Get a random witty response for a trigger word"""
    if trigger_word in WITTY_RESPONSES:
        return random.choice(WITTY_RESPONSES[trigger_word])
    return None


def get_welcome_message(user):
    """Get a random welcome message for new member"""
    message = random.choice(WELCOME_MESSAGES)
    return message.format(user=user.mention)


# SLASH COMMANDS
def process_mentions(message_text, guild):
    """Convert @123456789 format to proper Discord mentions"""
    import re

    # Pattern to find @followed by digits (user IDs)
    pattern = r'@(\d+)'

    def replace_mention(match):
        user_id = int(match.group(1))
        member = guild.get_member(user_id)
        if member:
            return member.mention
        else:
            # If user not found in guild, still create the mention format
            # Discord will show it as @invalid-user but it's better than leaving the ID
            return f'<@{user_id}>'

    # Replace all @userID with proper mentions
    processed_message = re.sub(pattern, replace_mention, message_text)
    return processed_message


@bot.slash_command(
    name="kpwrite",
    description="Send a message to general chat (Authorized user only)")
async def write_command(ctx, *, message: str):
    """Slash command to send messages to general chat - restricted to specific user and channel"""

    # Check if user is authorized
    if ctx.author.id != CONFIG["write_command_user_id"]:
        await ctx.respond(
            "❌ **Access Denied:** You are not authorized to use this command.",
            ephemeral=True)
        print(
            f"❌ Unauthorized /write attempt by {ctx.author} (ID: {ctx.author.id})"
        )
        return

    # Check if command is used in the correct channel
    if ctx.channel.id != CONFIG["write_command_channel_id"]:
        await ctx.respond(
            f"❌ **Wrong Channel:** This command can only be used in <#{CONFIG['write_command_channel_id']}>",
            ephemeral=True)
        print(
            f"❌ /write command used in wrong channel by {ctx.author} (Channel: {ctx.channel.name})"
        )
        return

    # Get the general channel (or fallback to welcome channel)
    target_channel_id = CONFIG.get("general_channel_id",
                                   CONFIG["welcome_channel_id"])
    target_channel = bot.get_channel(target_channel_id)

    # If configured channel not found, search for common general channel names
    if not target_channel:
        print(
            f"Target channel {target_channel_id} not found, searching for general channels..."
        )
        for channel_name in ['💬╭﹕general', 'general', 'main', 'chat', 'lobby']:
            target_channel = discord.utils.get(ctx.guild.text_channels,
                                               name=channel_name)
            if target_channel:
                print(f"Found general channel: #{target_channel.name}")
                break

    if not target_channel:
        await ctx.respond(
            "❌ **Error:** Could not find the general chat channel.",
            ephemeral=True)
        print("❌ Could not find general chat channel")
        return

    # Process the message to convert @userID to proper mentions
    processed_message = process_mentions(message, ctx.guild)

    try:
        # Send the processed message to general chat (anonymously)
        sent_message = await target_channel.send(processed_message)

        # Confirm to the user (privately) - minimal confirmation
        await ctx.respond("✅ **Message sent**", ephemeral=True)

        print(
            f"✅ Anonymous message sent to #{target_channel.name}: {processed_message[:50]}{'...' if len(processed_message) > 50 else ''}"
        )

    except discord.Forbidden:
        await ctx.respond(
            f"❌ **Permission Error:** Bot doesn't have permission to send messages in {target_channel.mention}",
            ephemeral=True)
        print(f"❌ No permission to send message in #{target_channel.name}")

    except discord.HTTPException as e:
        await ctx.respond(f"❌ **Error:** Failed to send message: {str(e)}",
                          ephemeral=True)
        print(f"❌ HTTP error sending message: {e}")

    except Exception as e:
        await ctx.respond(f"❌ **Unexpected Error:** {str(e)}", ephemeral=True)
        print(f"❌ Unexpected error in /write command: {e}")


@bot.slash_command(name="date",
                   description="Get current date in Nepali and English")
async def date_command(ctx):
    """Slash command to get current date and time"""
    try:
        from datetime import datetime
        import pytz

        # Get current time in Nepal timezone
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        now = datetime.now(nepal_tz)

        # English date
        english_date = now.strftime("%A, %B %d, %Y")
        english_time = now.strftime("%I:%M %p")

        # Nepali date mapping
        nepali_days = {
            'Monday': 'सोमबार',
            'Tuesday': 'मंगलबार',
            'Wednesday': 'बुधबार',
            'Thursday': 'बिहिबार',
            'Friday': 'शुक्रबार',
            'Saturday': 'शनिबार',
            'Sunday': 'आइतबार'
        }

        nepali_months = {
            'January': 'जनवरी',
            'February': 'फेब्रुअरी',
            'March': 'मार्च',
            'April': 'अप्रिल',
            'May': 'मे',
            'June': 'जुन',
            'July': 'जुलाई',
            'August': 'अगस्त',
            'September': 'सेप्टेम्बर',
            'October': 'अक्टोबर',
            'November': 'नोभेम्बर',
            'December': 'डिसेम्बर'
        }

        # Convert to Nepali
        day_name = now.strftime("%A")
        month_name = now.strftime("%B")
        nepali_day = nepali_days.get(day_name, day_name)
        nepali_month = nepali_months.get(month_name, month_name)

        # Format response
        date_response = f"""📅 **Current Date & Time:**

🇬🇧 **English:** {english_date}
🇳🇵 **Nepali:** {nepali_day}, {nepali_month} {now.day}, {now.year}

🕐 **Time:** {english_time} (Nepal Time)
🌍 **Timezone:** Asia/Kathmandu (NPT)"""

        await ctx.respond(date_response)
        print(f"✅ Date slash command executed successfully by {ctx.author}")

    except ImportError:
        error_msg = "❌ **Error:** pytz library not found. Please install it with: `pip install pytz`"
        await ctx.respond(error_msg)
        print("❌ pytz library not installed")
    except Exception as e:
        error_msg = f"❌ **Error:** Something went wrong: {str(e)}"
        await ctx.respond(error_msg)
        print(f"❌ Date command error: {e}")


@bot.slash_command(name="ping", description="Check if the bot is working")
async def ping_command(ctx):
    """Simple ping command to test slash commands"""
    latency = round(bot.latency * 1000)
    await ctx.respond(f"🏓 Pong! Bot latency: {latency}ms")
    print(f"✅ Ping command executed - Latency: {latency}ms")


@bot.slash_command(name="server_info",
                   description="Get information about this server")
async def server_info_command(ctx):
    """Get server information"""
    guild = ctx.guild

    server_info = f"""🏰 **Server Information:**

**Name:** {guild.name}
**ID:** {guild.id}
**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}
**Created:** {guild.created_at.strftime('%B %d, %Y')}
**Members:** {guild.member_count}
**Text Channels:** {len(guild.text_channels)}
**Voice Channels:** {len(guild.voice_channels)}
**Boost Level:** {guild.premium_tier}
**Boosts:** {guild.premium_subscription_count}"""

    await ctx.respond(server_info)
    print(f"✅ Server info command executed by {ctx.author}")


@bot.slash_command(
    name="reload_data",
    description="Reload bot responses from JSON file (Admin only)")
async def reload_data_command(ctx):
    """Reload bot data from JSON file"""
    if ctx.author.guild_permissions.administrator:
        try:
            reload_bot_data()
            await ctx.respond(
                f"✅ **Data reloaded!**\n📚 {len(TRIGGER_WORDS)} trigger words\n🎉 {len(WELCOME_MESSAGES)} welcome messages"
            )
            print(f"🔄 Data reloaded by {ctx.author}")
        except Exception as e:
            await ctx.respond(f"❌ **Reload failed:** {str(e)}")
            print(f"❌ Reload error: {e}")
    else:
        await ctx.respond("❌ Only administrators can reload data!")


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(f'Bot is ready to spread some wit! 🤖')
    print(f'Watching for these words: {", ".join(TRIGGER_WORDS)}')
    print(f'Connected to {len(bot.guilds)} servers:')

    for guild in bot.guilds:
        print(
            f'  - {guild.name} (ID: {guild.id}) - {guild.member_count} members'
        )

    # Check if member intent is working
    print(
        f'Members Intent: {"✅ ENABLED" if bot.intents.members else "❌ DISABLED"}'
    )
    print(
        f'Message Content Intent: {"✅ ENABLED" if bot.intents.message_content else "❌ DISABLED"}'
    )
    print('🎉 Welcome feature is active and waiting for new members!')

    # Print write command configuration
    print(f'\n📝 Write Command Configuration:')
    print(f'  - Authorized User ID: {CONFIG["write_command_user_id"]}')
    print(f'  - Command Channel ID: {CONFIG["write_command_channel_id"]}')
    print(
        f'  - Target Channel ID: {CONFIG.get("general_channel_id", CONFIG["welcome_channel_id"])}'
    )

    # Sync slash commands
    try:
        synced = await bot.sync_commands()
        if synced is not None:
            print(f"🔄 Synced {len(synced)} slash command(s)")
            print("Available slash commands:")
            for command in synced:
                print(f"  - /{command.name}: {command.description}")
        else:
            # Alternative method for older versions
            print("🔄 Attempting to sync slash commands...")
            print("Available slash commands:")
            for command in bot.pending_application_commands:
                print(f"  - /{command.name}: {command.description}")
            print("✅ Slash commands should be available in Discord")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        print("🔄 Trying alternative sync method...")
        try:
            # Manual sync for different discord.py versions
            await bot.sync_commands(force=True)
            print("✅ Force sync completed")
        except Exception as e2:
            print(f"❌ Alternative sync also failed: {e2}")
            print(
                "📝 Slash commands registered but may need manual server refresh"
            )

    print(
        'To test: try !debug-members command or add a new member to your server'
    )


@bot.event
async def on_member_join(member):
    """Welcome new members to the server"""
    print(f"\n{'='*50}")
    print(f"🎉 NEW MEMBER DETECTED: {member.name} (ID: {member.id})")
    print(f"Guild: {member.guild.name}")
    print(f"Member count now: {member.guild.member_count}")
    print(f"Time: {member.joined_at}")
    print(f"{'='*50}")

    # Get the welcome channel from config
    channel = bot.get_channel(CONFIG["welcome_channel_id"])
    print(f"Welcome channel: {channel}")

    # If no configured channel, find general channel
    if not channel:
        print("No configured channel found, searching for common channels...")
        for channel_name in [
                '💬╭﹕general', 'welcome', 'general', 'main', 'lobby'
        ]:
            channel = discord.utils.get(member.guild.text_channels,
                                        name=channel_name)
            if channel:
                print(f"Found channel: #{channel.name}")
                break

        if not channel:
            print("No common channels found, checking all channels...")
            # Print all available channels for debugging
            print("Available channels:")
            for ch in member.guild.text_channels:
                print(f"  - #{ch.name} (ID: {ch.id})")

    # If still no channel found, use first available text channel
    if not channel:
        if member.guild.text_channels:
            channel = member.guild.text_channels[0]
            print(f"Using first available channel: #{channel.name}")
        else:
            print("ERROR: No text channels found in server!")
            return

    # Send welcome message if channel is found
    if channel:
        welcome_msg = get_welcome_message(member)
        print(f"Attempting to send message: {welcome_msg}")
        try:
            sent_message = await channel.send(welcome_msg)
            print(
                f"✅ SUCCESS: Sent welcome message to {member.name} in #{channel.name}"
            )
            print(f"Message ID: {sent_message.id}")
        except discord.Forbidden:
            print(
                f"❌ PERMISSION ERROR: No permission to send message in #{channel.name}"
            )
            print(f"Bot permissions in #{channel.name}:")
            permissions = channel.permissions_for(member.guild.me)
            print(f"  - Send Messages: {permissions.send_messages}")
            print(f"  - View Channel: {permissions.view_channel}")
            print(
                f"  - Read Message History: {permissions.read_message_history}"
            )
        except discord.HTTPException as e:
            print(f"❌ HTTP ERROR: {e}")
        except Exception as e:
            print(f"❌ UNKNOWN ERROR: {e}")
    else:
        print("❌ CRITICAL: No suitable channel found for welcome message")

    print(f"{'='*50}\n")


@bot.event
async def on_message(message):
    # Don't respond to our own messages
    if message.author == bot.user:
        return

    # Don't respond to other bots
    if message.author.bot:
        return

    # Check if specific user is mentioned
    SAMU_USER_ID = CONFIG["samu_user_id"]
    if any(user.id == SAMU_USER_ID
           for user in message.mentions) and not message.reference:
        # React with a random emoji when the specific user is tagged
        samu_tag_reactions = CONFIG["samu_tag_reactions"]
        reaction_emoji = random.choice(samu_tag_reactions)
        await message.add_reaction(reaction_emoji)
        print(f"Added {reaction_emoji} reaction - specific user was mentioned")

    # Simple help command
    if message.content.lower() == '!help':
        help_text = f"I'm a witty bot! I respond to these words: {', '.join(TRIGGER_WORDS)}\n"
        help_text += "Just use any of these words in your message and I'll drop some wisdom! 🧠✨\n"
        help_text += "**Text Commands:** !help, !words, !test-welcome, !debug-members, !force-welcome, !sync-commands, !reload-data\n"
        help_text += "**Slash Commands:** /date, /ping, /server_info, /reload_data, /write"
        await message.channel.send(help_text)
        return

    # Add word command to show trigger words
    if message.content.lower() == '!words':
        word_list = "📝 **Current trigger words:**\n" + "\n".join(
            [f"• {word}" for word in TRIGGER_WORDS])
        await message.channel.send(word_list)
        return

    # Reload data command (text version)
    if message.content.lower() == '!reload-data':
        if message.author.guild_permissions.administrator:
            try:
                reload_bot_data()
                await message.channel.send(
                    f"✅ **Data reloaded!**\n📚 {len(TRIGGER_WORDS)} trigger words\n🎉 {len(WELCOME_MESSAGES)} welcome messages"
                )
                print(f"🔄 Data reloaded by {message.author}")
            except Exception as e:
                await message.channel.send(f"❌ **Reload failed:** {str(e)}")
                print(f"❌ Reload error: {e}")
        else:
            await message.channel.send("❌ Only administrators can reload data!"
                                       )
        return

    # Test welcome message command
    if message.content.lower() == '!test-welcome':
        test_welcome = get_welcome_message(message.author)
        await message.channel.send(
            f"🧪 **Test Welcome Message:**\n{test_welcome}")

        # Also check member intent status
        if bot.intents.members:
            intent_status = "✅ Server Members Intent is ENABLED"
        else:
            intent_status = "❌ Server Members Intent is DISABLED"

        await message.channel.send(
            f"**Debug Info:**\n{intent_status}\nGuild member count: {message.guild.member_count}"
        )
        return

    # Debug command to check member events AND slash commands
    if message.content.lower() == '!debug-members':
        # Get registered slash commands
        slash_commands = bot.pending_application_commands
        slash_list = "\n".join([
            f"• /{cmd.name}: {cmd.description}" for cmd in slash_commands
        ]) if slash_commands else "• No slash commands found"

        debug_info = f"""**🔍 Bot Debug Information:**

**Intents Status:**
• Members Intent: {"✅ ENABLED" if bot.intents.members else "❌ DISABLED"}
• Message Content Intent: {"✅ ENABLED" if bot.intents.message_content else "❌ DISABLED"}

**Server Info:**
• Server: {message.guild.name}
• Member Count: {message.guild.member_count}
• Bot ID: {bot.user.id}

**Data Status:**
• Trigger Words: {len(TRIGGER_WORDS)}
• Welcome Messages: {len(WELCOME_MESSAGES)}
• Config Settings: {len(CONFIG)}

**Write Command Config:**
• Authorized User ID: {CONFIG["write_command_user_id"]}
• Command Channel ID: {CONFIG["write_command_channel_id"]}
• Target Channel ID: {CONFIG.get("general_channel_id", CONFIG["welcome_channel_id"])}

**Registered Slash Commands:**
{slash_list}

**Events Status:**
• on_ready: ✅ Working
• on_message: ✅ Working (you're seeing this!)
• on_member_join: ❓ Test by adding new member

**Troubleshooting:**
• If slash commands don't appear, try: `!sync-commands` (admin only)
• To reload responses: `!reload-data` or `/reload_data` (admin only)
• Wait 1-2 minutes after sync for commands to appear
• Try typing `/` in Discord to see available commands
• Bot needs "Use Slash Commands" permission

**Test Commands:**
• !force-welcome - Test welcome message
• !sync-commands - Force sync slash commands (admin)
• !reload-data - Reload responses from JSON (admin)
• /date - Get current date/time
• /ping - Test bot latency
• /server_info - Server information
• /write - Send message to general (authorized user only)
        """
        await message.channel.send(debug_info)
        return

    # Force member join test command (for debugging)
    if message.content.lower() == '!force-welcome':
        # This simulates the welcome message as if the user just joined
        print(f"🧪 MANUAL WELCOME TEST triggered by {message.author}")
        channel = message.channel
        welcome_msg = get_welcome_message(message.author)
        await channel.send(f"**[MANUAL TEST]** {welcome_msg}")
        print(f"✅ Manual welcome test completed")
        return

    # Manual slash command sync (admin only)
    if message.content.lower() == '!sync-commands':
        if message.author.guild_permissions.administrator:
            try:
                synced = await bot.sync_commands()
                if synced is not None:
                    await message.channel.send(
                        f"✅ Synced {len(synced)} slash commands!")
                else:
                    await message.channel.send(
                        "✅ Slash commands synced (no count available)")
                print(f"🔄 Manual sync triggered by {message.author}")
            except Exception as e:
                await message.channel.send(f"❌ Sync failed: {str(e)}")
                print(f"❌ Manual sync error: {e}")
        else:
            await message.channel.send(
                "❌ Only administrators can sync commands!")
        return

    # Check if message contains any trigger words
    trigger_words = find_trigger_words(message.content)

    if trigger_words:
        # Pick a random trigger word if multiple found
        chosen_word = random.choice(trigger_words)
        response = get_witty_response(chosen_word)

        if response:
            # Add some variety - sometimes mention the user, sometimes add emoji reactions
            if random.random() < 0.2:  # 20% chance to mention the user
                response = f"{message.author.mention} {response}"

            await message.channel.send(response)

            # Sometimes add a reaction emoji for extra personality
            if random.random() < 0.1:  # 10% chance to add reaction
                reactions = CONFIG["general_reactions"]
                await message.add_reaction(random.choice(reactions))

            print(
                f"Responded to '{chosen_word}' in message from {message.author}: '{message.content[:50]}...'"
            )

    # Process commands
    await bot.process_commands(message)


try:
    token = os.getenv("TOKEN") or ""
    if token == "":
        raise Exception("Please add your token to the Secrets pane.")
    bot.run(token)
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
