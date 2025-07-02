# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import os
import discord
import random
import re
from discord.ext import commands

# Enable message content intent to read message content
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable member events

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary of trigger words/phrases and their witty Nepali responses
WITTY_RESPONSES = {
    "monday": [
        "Monday? Aja feri suru! Jindagi ko struggle aja dekhi 😴",
        "Monday lai Saturday sanga replace garna milthyo ni! 📅",
        "Arko hapta ko countdown suru! Monday blues attack! 🥲"
    ],
    "coffee": [
        "Chiya bina jindagi incomplete! Coffee pani chalcha hai ☕",
        "Morning ko energy source: Coffee/Chiya - choose your fighter! ☕",
        "Caffeinated bhayera matra human form ma aaunchu ma! 🤖☕"
    ],
    "tired": [
        "Thakeko? Mobile ko battery jastai low power mode ma! 🔋",
        "Tired vanna lai 'Thakaye' vannu paryo! Nepali ma sounds better! 😴",
        "Energy tira gayera aaija, thaki haleko jasto cha! ⚡"
    ],
    "homework": [
        "Homework = Ghar ko kaam. Teacher haru ko creative torture method! 📚",
        "Homework garne bela: 'Kina padhdai chu ma?' philosophical crisis! 🤔",
        "School ma 6 ghanta, ghar ma homework - when does childhood happen? 😅"
    ],
    "work": [
        "Kaam ko pressure ma sabai same - 'Paisa kamaunu paryo' syndrome! 💼",
        "Work from home vs Office - same kaam, different location, same stress! 🏠💻",
        "Monday dekhi Friday - survival mode ON! Weekend ko sapana! 🥱"
    ],
    "exam": [
        "Exam = Extreme Anxiety Mode activated! Padhdeko kei yaad chaina! 📖",
        "Exam hall ma: 'Yo ta sikaako thiyena ni sir le!' panic attack! 😰",
        "Good luck! Pass vaye celebrate, fail vaye... 'next time better' vanne! 🤞"
    ],
    "food": [
        "Khana ko kura bhayo? Dal bhat power, 24 hour! 🍚",
        "Momo vs Pizza - eternal debate! But both are life! 🥟🍕",
        "Khana khayera khushi, na khayera dukhhi - simple logic! 😋"
    ],
    "weather": [
        "Weather in Nepal: Summer ma garmi, winter ma jado - predictable unpredictability! 🌦️",
        "Barsa aayo ki load shedding, winter aayo ki blanket - seasonal routine! ⛅",
        "Kathmandu ko weather: confused, just like all of us! 🤷‍♂️"
    ],
    "test": [
        "Test bhanne sabda le stress level 100% increase garchha! 📋",
        "Test ma: A, B, C, D - eeny meeny miny mo technique! 🎯",
        "Internal exam, terminal exam - exam ko museum banako jasto! 📝"
    ],
    "momo": [
        "Momo = Nepali ko pride! Argument garna milena yo topic ma! 🥟",
        "Jhol momo vs Fried momo - tough choice, better order both! 🥟🔥",
        "World peace achieve garna cha? Sabai lai momo khuwaideu! 🌍🥟"
    ],
    "dal": [
        "Dal bhat tarkari - Trinity of Nepali cuisine! ⚡",
        "Dal bhat khayera Everest climb garna sakiyo vane... possible! 🏔️",
        "Dal bhat power ho, 24 hour! Slogan nai perfect cha! 💪"
    ],
    "traffic": [
        "Kathmandu ko traffic: meditation practice ho, patience sikauchha! 🚗🙏",
        "Ring road ma stuck - time travel experience, past ma janchha! ⏰",
        "Traffic jam ma book padhna milchha, skill development! 📚🚌"
    ],
    "load": [
        "Load shedding ko memories: candle, study lamp, family bonding time! 🕯️",
        "Generator, inverter, solar - load shedding le innovative banayo! ⚡",
        "Load gayo bhane - unexpected holiday feeling! 💡"
    ],
    "festival": [
        "Dashain, Tihar, Holi - festival season ma wallet empty! 🎉💸",
        "Festival ma: khana, nachana, relatives - complete package! 🎊",
        "Nepali festivals: culture, tradition, ani ali ali hangover! 🎭"
    ],
    "bus": [
        "Public bus: adventure sport ho Nepal ma! Seat paucha ki napauchha! 🚌",
        "Bus ma: 'Bhai roknus' vanera haath hilauney skill develop huncha! 🖐️",
        "Microbus vs Bus - same destination, different level of compression! 😅"
    ],
    "bike": [
        "Bike chalauney vs Bus ma janey - fuel vs patience ko trade-off! 🏍️",
        "Kathmandu ma bike = traffic ninja mode activated! 🥷",
        "Bike ma helmet lagayera safety first, style second! ⛑️"
    ],
    "internet": [
        "Internet slow vayo ki life slow huncha! Wi-Fi = life support! 📶",
        "Data sakiyo = social isolation mode ON! Top up garnu parne! 📱",
        "Broadband vs Mobile data - monthly budget planning skill! 💸"
    ],
    "phone": [
        "Phone battery 10% = emergency mode, sab kaam fast garnuparyo! 🔋",
        "Phone upgrade garnu parne ki loan linu parne dilemma! 📱💭",
        "Phone case lagayera accident bata bachaunuparyo - insurance ho! 📱🛡️"
    ],
    "money": [
        "Paisa = happiness equation solve garney key factor! 💰",
        "Month end ma: 'Kaha gayo sab paisa?' mystery solving time! 🔍💸",
        "ATM queue ma basda patience level increase huncha! 🏧⏰"
    ],
    "salary": [
        "Salary credit vayo notification = month ko sabse khushi moment! 💳✨",
        "Salary vs Expenses - mathematical equation kabhi balance hudaina! 📊",
        "Increment ko sapana = lottery ticket jitney hope! 💸🎟️"
    ],
    "college": [
        "College life: padhai, friends, ani 'future kasto hola?' tension! 🎓",
        "College canteen ko khana = survival food, taste secondary! 🍛",
        "Assignment deadline = time management skill forced development! 📝⏰"
    ],
    "teacher": [
        "Teacher lai respect, but sometimes 'kina yesto question sodheko?' 👨‍🏫",
        "Good teacher = life changer, boring teacher = sleep inducer! 😴📚",
        "Online class vs Physical class - teacher ko struggle doubled! 💻🎭"
    ],
    "friend": [
        "True friend = momo treat gardine, fake friend = split the bill! 🥟💰",
        "Friend zone = Nepal ma pani exist garchha, worldwide problem! 😅❤️",
        "Childhood friend vs College friend - different category, same love! 👫"
    ],
    "movie": [
        "Nepali movie vs Bollywood vs Hollywood - mood anusar choice! 🎬",
        "Cinema hall ma janey vs OTT ma herney - budget vs experience! 🍿📱",
        "Movie recommendation = friend circle ko heated debate topic! 🎭"
    ],
    "cricket": [
        "Cricket = Nepal ko passion! Every gully ma future Paras Khadka! 🏏",
        "World Cup time ma office productivity zero, TV ma focus 100%! 📺⚡",
        "Cricket debate = friendship test, team support serious matter! 🤝⚾"
    ],
    "football": [
        "Football vs Cricket debate = never ending story in Nepal! ⚽🏏",
        "European football dekhda: 'Nepal ma pani yesto team bhayethyo!' 🌍⚽",
        "Football boots vs Cricket bat - sports equipment investment! 👟🏏"
    ],
    "shopping": [
        "Window shopping vs Real shopping - different economic categories! 🛍️👀",
        "New Road, Asan Bazar - shopping destination variety pack! 🏪",
        "Online shopping vs Physical shopping - convenience vs touch and feel! 📦🛒"
    ],
    "rent": [
        "Rent = monthly heartbreak, paisa udaune fixed schedule! 🏠💸",
        "Good location vs Cheap rent - life ko major compromise! 📍💰",
        "Landlord relationship = diplomatic skill develop garna parney! 🤝🏠"
    ],
    "hotel": [
        "Dal bhat hotel vs fancy restaurant - pocket anusar choice! 🍽️💰",
        "Hotel ko khana vs Ghar ko khana - taste vs convenience battle! 🏠🍛",
        "Menu herda: 'Rs. 500 for this?' price shock syndrome! 📋💸"
    ],
    "corona": [
        "Corona time ma mask = new fashion accessory ban gayo! 😷✨",
        "Lockdown ma: Netflix, cooking, family bonding - forced quality time! 🏠📺",
        "Sanitizer ko smell = 2020-2023 ko memory trigger! 🧴👃"
    ],
    "vaccine": [
        "Vaccine lagayera superhero feel! Immunity boost activated! 💉⚡",
        "First dose vs Second dose - countdown to normal life! 💉✅",
        "Vaccine certificate = travel passport ban gayo temporarily! 📋✈️"
    ],
    "hospital": [
        "Hospital jane dar vs Health checkup importance - adult dilemma! 🏥⚖️",
        "Queue ma wait garney patience = hospital le sikauchha! 🏥⏰",
        "Medicine expensive, health priceless - economy vs biology! 💊💰"
    ],
    "cringe":
    ["Bold words from someone whose personality came from a group chat."]
}

# Words that should trigger a response (case-insensitive)
TRIGGER_WORDS = list(WITTY_RESPONSES.keys())

# Welcome messages for new members
WELCOME_MESSAGES = [
    "Welcome to Oli Bois {user}! — no rules, just vibes.",
    "You've officially entered the boi-zone {user}!",
    "This server is powered by beer, smokes, and chaos {user}!",
    "Welcome to the Oli Bois madhouse {user}! — leave your logic outside.",
    "Smoking? Drinking? Gaming? Perfect {user}! You belong here.",
    "Congratulations {user}!, you're now one of the degens.",
    "Oli Bois ain't a server, it's a whole damn vibe {user}!",
    "Grab a chair, light a cig, game on — welcome {user}!",
    "Welcome to the chill zone with zero chill {user}!",
    "We don't do normal here {user}! — welcome to the jungle.",
    "One of us, one of us — welcome, legend {user}!",
    "If you're reading this {user}!, you're already too deep.",
    "Oli Bois — where the pixels are lit and so are we {user}!",
    "Welcome to Oli Bois {user}!: the land of late nights and worse decisions.",
    "No entry fee, just pure madness {user}!",
    "This is your last stop before normalcy disappears {user}!",
    "Gaming, gossip, ganja — you're home now {user}!",
    "Say goodbye to productivity {user}! — Oli Bois just claimed you.",
    "This is where the chaos feels cozy {user}!",
    "Your sanity ends here — welcome {user}!",
    "Oli Bois: Not responsible for any hangovers {user}!",
    "Welcome, stranger {user}!. Take a shot, sit back.",
    "Make memes, not sense — that's how we do it {user}!",
    "10% game, 90% stupidity — 100% fun {user}!",
    "From Nepal to nowhere — Oli Bois rise {user}!",
    "Keep your volume low, the chaos is loud {user}!",
    "Welcome {user}! — hope your therapist is on speed dial.",
    "Log in, light up, level up {user}!",
    "One server to rule them all — and roast them all {user}!",
    "Welcome to Oli Bois {user}! — where the party never loads properly.",
    "Warning: This server contains high doses of dumb {user}!",
    "Leave your seriousness at the door {user}!",
    "Entry granted {user}!. IQ dropped instantly.",
    "Oli Bois — like your group chat, but unfiltered {user}!",
    "Welcome to where plans die and memes thrive {user}!",
    "Beer in one hand, controller in the other {user}!",
    "This isn't Discord, this is dis-chaos {user}!",
    "Come for the games, stay for the bullshit {user}!",
    "You have entered a no-sleep zone {user}!",
    "All-night chaos? Just another Tuesday here {user}!",
    "Welcome to the unholy combo of fun and regret {user}!",
    "Oli Bois — putting the 'lit' in 'legitimately insane' {user}!",
    "One server. Infinite vibes {user}!",
    "Welcome to where energy drinks cry for mercy {user}!",
    "Friends don't let friends stay sober on voice chat {user}!",
    "You thought you were normal? Cute {user}!",
    "Come as you are — leave as an Oli Boi {user}!",
    "Bro, you in? You in {user}!",
    "Where every 'yo' leads to a 5-hour call {user}!",
    "Welcome {user}! — now get weird with us.",
    "We're not toxic, we're spicy {user}!",
    "Welcome to the server that your mom warned you about {user}!",
    "Oli Bois: Because adulting is overrated {user}!",
    "We game hard, laugh harder {user}!", "Keep calm and spam emojis {user}!",
    "Come for the memes, stay for the late-night philosophy {user}!",
    "Oli Bois — breaking TOS since forever {user}!",
    "Enter the server, lose the plot {user}!",
    "We put the 'cha' in 'chat' {user}!",
    "Welcome to where drama is content {user}!",
    "Oli Bois: The only place lag is a lifestyle {user}!",
    "We don't crash games, we crash each other {user}!",
    "One chat, too many egos {user}!",
    "No cap, this server is cracked {user}!",
    "Welcome {user}! — we've been expecting your nonsense.",
    "Respect is earned. But here? Just be funny {user}!",
    "Sleep? We left that at the gate {user}!",
    "Welcome to the server that runs on caffeine and trauma {user}!",
    "Oli Bois: where plans get made and forgotten {user}!",
    "Enter loud, leave louder {user}!",
    "Let the games begin (and the braincells die) {user}!",
    "If stupidity was a server, it'd be this {user}!",
    "Welcome, soldier of chaos {user}!",
    "This ain't a phase, it's a lifestyle {user}!",
    "From lol to lmao — welcome aboard {user}!",
    "Welcome to where weekdays feel like weekends {user}!",
    "Oli Bois — we peak at 3 a.m. {user}!",
    "Welcome to where 'yo' means 20 things {user}!",
    "You just joined the most elite squad of nobodies {user}!",
    "Congrats {user}!! You made it to the bad decision zone.",
    "Don't ask for rules. There aren't any {user}!",
    "If you're here, you're already doomed (in the best way) {user}!",
    "Oli Bois is 90% noise and 10% more noise {user}!",
    "This server is sponsored by vibes and vapes {user}!",
    "Welcome to where everyone's mic is always cursed {user}!",
    "Game night? More like roast night {user}!",
    "Enter a chat, leave with trauma {user}!",
    "We put the 'bro' in broken sleep schedules {user}!",
    "It's not a cult. Yet {user}!",
    "Server motto: vibe hard, crash harder {user}!",
    "Welcome to the Nepali Avengers of Discord {user}!",
    "Your life just got significantly more unhinged {user}!",
    "Bring your problems — we'll roast them {user}!",
    "Welcome {user}! — now earn your nickname.",
    "Oli Bois — because therapy is expensive {user}!",
    "This is not a drill. This is real, chaotic energy {user}!",
    "In this server, everyone's a main character {user}!",
    "The lights are neon, the vibes are feral {user}!",
    "Type faster — the madness awaits {user}!",
    "Welcome, legend {user}!! You just joined the most gloriously useless server ever."
]


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


@bot.slash_command(name="date",
                   description="Get current date in Nepali and English")
async def date_command(ctx):
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

    # Get the system channel (default channel for welcome messages)
    channel = bot.get_channel(762775973816696863)
    print(f"System channel: {channel}")

    # If no system channel, try to find a general channel
    if not channel:
        print("No system channel found, searching for common channels...")
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

    # If still no channel found, use the first available text channel
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
    SPECIFIC_USER_ID = 783619741289414676  # Replace with the actual user ID
    if any(user.id == SPECIFIC_USER_ID
           for user in message.mentions) and not message.reference:
        # React with a random emoji when the specific user is tagged
        tag_reactions = [
            '🙈', '<:aww:786672671928614933>',
            '<a:flyingkisses:798813605033672714>'
        ]
        reaction_emoji = random.choice(tag_reactions)
        await message.add_reaction(reaction_emoji)
        print(f"Added {reaction_emoji} reaction - specific user was mentioned")

    # Simple help command
    if message.content.lower() == '!help':
        help_text = f"I'm a witty bot! I respond to these words: {', '.join(TRIGGER_WORDS)}\n"
        help_text += "Just use any of these words in your message and I'll drop some wisdom! 🧠✨\n"
        help_text += "Commands: !help, !words, !test-welcome, !debug-members, !force-welcome\n"
        help_text += "Slash Commands: /date"
        await message.channel.send(help_text)
        return

    # Add word command to add trigger words dynamically
    if message.content.lower() == '!words':
        word_list = "📝 **Current trigger words:**\n" + "\n".join(
            [f"• {word}" for word in TRIGGER_WORDS])
        await message.channel.send(word_list)
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

    # Debug command to check member events
    if message.content.lower() == '!debug-members':
        debug_info = f"""**🔍 Member Event Debug Info:**

**Intents Status:**
• Members Intent: {"✅ ENABLED" if bot.intents.members else "❌ DISABLED"}
• Message Content Intent: {"✅ ENABLED" if bot.intents.message_content else "❌ DISABLED"}

**Server Info:**
• Server: {message.guild.name}
• Member Count: {message.guild.member_count}
• Bot ID: {bot.user.id}

**Events Status:**
• on_ready: ✅ Working
• on_message: ✅ Working (you're seeing this!)
• on_member_join: ❓ Test by adding new member

**Slash Commands:**
• /date: ✅ Available

**Test Instructions:**
1. Add a new Discord account to this server
2. Check console logs for member join detection
3. Or try !force-welcome for manual test
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
                reactions = ['😂', '👍', '🤔', '😎', '🔥', '✨']
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
