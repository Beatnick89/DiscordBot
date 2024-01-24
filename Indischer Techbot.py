import os
import discord
import random
import json
import atexit
from willkommen import welcome_messages
from dotenv import load_dotenv
from discord.ext import commands
from requests import get
from responses import get_response
from jokes import get_joke
from emojidb import emojis

# Token loader
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Bot Setup
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command("help")

# Response Funktion
async def send_message(message, user_message):
    if user_message and (is_private := user_message[0] == '?'):
        user_message = user_message[1:]

    try:
        response = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# Member Join
@bot.event
async def on_member_join(member):
    if (guild := member.guild).system_channel is not None:
        welcome_message = random.choice(welcome_messages).format(member=member, guild=guild)
        await guild.system_channel.send(welcome_message)

# Constants
TARGET_CHANNEL_NAME = '🔊｜Join to create'
target_channel_ids = []
TARGET_CHANNEL_FILE = 'target_channel_ids.json'
try:
    with open(TARGET_CHANNEL_FILE, 'r') as file:
        data = file.read()
        if data:
            target_channel_ids = json.loads(data)
except (FileNotFoundError, json.JSONDecodeError):
    pass
def save_target_channel_ids():
    with open(TARGET_CHANNEL_FILE, 'w') as file:
        json.dump(target_channel_ids, file)
atexit.register(save_target_channel_ids)
# Create voice
@bot.command(name='create_voice', help='Create a join-to-create voice channel (Admin Only)')
async def create_voice(ctx):
    try:
        admin_role = discord.utils.get(ctx.guild.roles, name='Admin')
        if admin_role and admin_role in ctx.author.roles:
            voice_category = discord.utils.get(ctx.guild.categories, name='Voice Channels')
            channel_name = f"{TARGET_CHANNEL_NAME}"
            voice_channel = await ctx.guild.create_voice_channel(channel_name, category=voice_category)
            target_channel_ids.append(voice_channel.id)  # Use the ID of the created channel

            await ctx.send(f"{TARGET_CHANNEL_NAME} channel created.")
        else:
            await ctx.send("You do not have the admin role to create voice channels.")
    except Exception as e:
        print(f"Failed to create voice channel: {e}")
# Voice Channel Management
temp_channels = {}
@bot.event
async def on_voice_state_update(member, before, after):
    user_display_name = member.display_name or member.name

    if after.channel and after.channel.id in target_channel_ids:
        temp_channel = await after.channel.clone(name=f"{user_display_name}'s area")
        await member.move_to(temp_channel)
        temp_channels[member.id] = temp_channel.id

    if before.channel and before.channel.id in temp_channels.values():
        await before.channel.delete()
        temp_channels.pop(member.id, None)
@bot.event
async def on_disconnect():
    save_target_channel_ids()

#Pin Function
@bot.command(name='pin', help='Pin eine Nachricht')
async def pin_message(ctx, *args):
    admin_role = discord.utils.get(ctx.guild.roles, name='Admin')  # Replace 'Admin' with your actual admin role name
    if admin_role and admin_role in ctx.author.roles:
        message_content = ' '.join(args)
        await ctx.message.delete()
        sent_message = await ctx.send(message_content)
        await sent_message.pin()

        success_message = f'Nachricht erfolgreich angepinnt {ctx.author.display_name}!'
        success_comment = await ctx.send(success_message)
        await success_comment.delete(delay=2)
    else:
        await ctx.send("Du hast nicht die passenden Rechte")

# Insert new function here

#Voteing Funktion
@bot.command(name='vote', help='Erstelle eine Abstimmungsnachricht')
async def vote(ctx, title, option1, option2):
    admin_role = discord.utils.get(ctx.guild.roles, name='Admin')
    if admin_role and admin_role in ctx.author.roles:
        embed = discord.Embed(title=title, color=discord.Color.blue())
        embed.add_field(name='Option 1', value=option1, inline=False)
        embed.add_field(name='Option 2', value=option2, inline=False)

        message = await ctx.send(embed=embed)
        await message.add_reaction('1️⃣')
        await message.add_reaction('2️⃣')

    else:
        await ctx.send("Du hast nicht die passenden Rechte")

    await ctx.message.delete()

#Move LootCouncil
@bot.command(name='council', help='Move members with "council" role to a specific channel')
async def council(ctx):
    admin_role = discord.utils.get(ctx.guild.roles, name='council')

    if admin_role and admin_role in ctx.author.roles:
        council_role = discord.utils.get(ctx.guild.roles, name='council')
        target_channel_id = 1103003718397468707  # Replace with the ID of the target channel

        if council_role is not None:
            members_with_council_role = [member for member in ctx.guild.members if council_role in member.roles]

            for member in members_with_council_role:
                try:
                    target_channel = ctx.guild.get_channel(target_channel_id)
                    await member.move_to(target_channel)
                    await ctx.send(f"Moved {member.display_name} to {target_channel.name}")
                except Exception as e:
                    print(f"Failed to move {member.display_name}: {e}")
        else:
            await ctx.send("Das Council gibt es noc nicht.")
    else:
        await ctx.send("Du bist kein Mitglied vom  Councils.")

#Roll reaction Function
role_embed_message_id = None
@bot.command(name='role')
async def role(ctx):
    admin_role = discord.utils.get(ctx.guild.roles, name='Admin')
    global role_embed_message_id

    if "admin" in [role.name.lower() for role in ctx.author.roles]:
        role_embed = discord.Embed(
            title="Klick auf eine Reaction um eine Rolle auszuwählen",
            color=discord.Colour.random())

        for emoji, role_name in emojis:
            role_embed.add_field(name=role_name, value=emoji, inline=False)

        if role_embed_message_id:
            try:
                message = await ctx.fetch_message(role_embed_message_id)
                await message.edit(embed=role_embed)
            except discord.errors.NotFound:
                message = await ctx.send(embed=role_embed)
                role_embed_message_id = message.id
        else:
            message = await ctx.send(embed=role_embed)
            role_embed_message_id = message.id

        for emoji, _ in emojis:
            try:
                await message.add_reaction(emoji)
            except discord.errors.HTTPException as e:
                print(f"Failed to add reaction: {e}")
    else:
        await ctx.send("You do not have permission to use this command.")
# Add Reaction Roles
@bot.event
async def on_raw_reaction_add(payload):
    global role_embed_message_id

    message_id = payload.message_id
    if message_id == role_embed_message_id:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)

        role = discord.utils.get(guild.roles, name=payload.emoji.name)

        if role is not None:
            member = guild.get_member(payload.user_id)
            if member is not None:
                await member.add_roles(role)
# Remove Reaction Roles
@bot.event
async def on_raw_reaction_remove(payload):
    global role_embed_message_id

    message_id = payload.message_id
    if message_id == role_embed_message_id:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)

        role = discord.utils.get(guild.roles, name=payload.emoji.name)

        if role is not None:
            member = guild.get_member(payload.user_id)
            if member is not None:
                await member.remove_roles(role)

#Admin Help
def get_adminhelp_embed(ctx):
    help_embed = discord.Embed(title="Help Desk for Admins",
                               description="All Admin commands for the bot.",
                               color=discord.Colour.random())

    help_embed.set_author(name="Tech Bot", icon_url=ctx.bot.user.avatar)
    help_embed.add_field(name="role", value="platziert Role Embed (bitte nicht  nutzen)", inline=False)
    help_embed.add_field(name="pin", value="!pin <Hier die Nachricht die gepinnt werden soll>", inline=False)
    help_embed.add_field(name="council", value="Ruft das Loot Council zusammen nur nutzbar als Council Mitglied", inline=False)
    help_embed.add_field(name="vote", value='!voting "Voting Title" "Option 1" "Option 2"', inline=False)
    help_embed.add_field(name="create_voice", value="Erstellt Join to create Channel", inline=False)
    help_embed.add_field(name="Need Help?", value="Ask .beatnick on Discord", inline=False)
    help_embed.set_footer(text=f"Requested by {ctx.author.display_name}.", icon_url=ctx.author.avatar)

    return help_embed
@bot.command(name='adminhelp', help='Display custom admin help information')
async def adminhelp_command(ctx):
    # Check if the user has the admin role
    admin_role = discord.utils.get(ctx.guild.roles, name='Admin')  # Replace 'admin' with your actual admin role name
    if admin_role and admin_role in ctx.author.roles:
        adminhelp_embed = get_adminhelp_embed(ctx)
        await ctx.send(embed=adminhelp_embed)
    else:
        await ctx.send("You do not have permission to use this command.")
#Normal Help
@bot.command(name='help', help='Display custom help information')
async def help_command(ctx):
    help_embed = discord.Embed(title="Help Desk",
                               description="General help information for the bot.",
                               color=discord.Colour.random())

    help_embed.set_author(name="Tech Bot", icon_url=ctx.bot.user.avatar)
    help_embed.add_field(name="roll", value="rollen", inline=False)
    help_embed.add_field(name="Test", value="Delete", inline=False)
    help_embed.add_field(name="Khorne", value="Blood for the Blood God", inline=False)
    help_embed.add_field(name="Witz", value="Erzählt einen Witz", inline=False)
    help_embed.add_field(name="Ping", value="Pong", inline=False)
    help_embed.add_field(name="Need Help?", value="Ask .beatnick on Discord", inline=False)
    help_embed.set_footer(text=f"Requested by {ctx.author.display_name}.", icon_url=ctx.author.avatar)

    await ctx.send(embed=help_embed)

# Startup für den Bot
@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')

# Inc Messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        username = str(message.author)
        user_message = message.content[1:]
        channel = str(message.channel)


        if not user_message.lower().startswith(('help', 'role', 'meme', 'pin',
                                                'adminhelp', 'council', 'embed',
                                                'vote','create_voice', 'feedback')):
            await send_message(message, user_message)


    if message.content.startswith('?witz'):
        joke = get_joke()
        print(joke)

        if joke is False:
            await message.channel.send("Couldn't get joke from API. Try again later.")
        else:
            await message.channel.send(joke['setup'] + '\n' + joke['punchline'])

    await bot.process_commands(message)

# Main entry
if __name__ == '__main__':
    bot.run(TOKEN)
