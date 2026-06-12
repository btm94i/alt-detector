# This example requires the 'members' and 'message_content' privileged intents to function.

import os
import random
import sqlite3
import uuid

import discord
import dotenv
from discord.ext import commands

description = """An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here."""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

db = sqlite3.connect("data.db")

bot = commands.Bot(command_prefix="?", description=description, intents=intents)

dotenv.load_dotenv()


@bot.event
async def on_ready():
    # Tell the type checker that User is filled up at this point
    assert bot.user is not None

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.event
async def on_member_join(member: discord.Member):
    memberid = member.id
    # Check if known member
    result = db.execute("SELECT * FROM known_members WHERE id = ?", (memberid,))
    if result.fetchone() is not None:
        await member.add_roles(discord.Object(id=1514957798654476398))
    else:
        await member.send(
            "Please verify your account by typing `?verify` in the server."
        )


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split("d"))
    except Exception:
        await ctx.send("Format has to be in NdN!")
        return

    result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(description="For when you wanna settle the score some other way")
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content="repeating..."):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)


def generate_session_id() -> str:
    return str(uuid.uuid1())


@bot.command()
async def verify(ctx):
    """Verifies the user."""
    session_id = generate_session_id()
    await ctx.send(f"http://localhost:8000/verify/{session_id}")


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    # Joined at can be None in very bizarre cases so just handle that as well
    if member.joined_at is None:
        await ctx.send(f"{member} has no join date.")
    else:
        await ctx.send(f"{member} joined {discord.utils.format_dt(member.joined_at)}")


@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f"No, {ctx.subcommand_passed} is not cool")


@cool.command(name="bot")
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send("Yes, the bot is cool.")


bot.run(str(os.getenv("BOT_TOKEN")))
