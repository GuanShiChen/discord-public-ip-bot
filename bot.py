import discord
from discord.ext import commands
import requests
import asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# --- Configuration ---
IP_FILE = "public_ip.txt"
IP_API_URL = "https://api.ipify.org"
MIN_INTERVAL_SECONDS = 1
MAX_INTERVAL_SECONDS = 7200

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- Global State ---
interval_seconds = 300
current_user_mention = bot.user.mention if bot.user else ""
running = True


# --- Helper Functions ---

def get_public_ip():
    try:
        response = requests.get(IP_API_URL, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        return None
    except requests.RequestException:
        return None


def read_saved_ip():
    if not os.path.exists(IP_FILE):
        return None
    try:
        with open(IP_FILE, "r") as f:
            return f.read().strip()
    except:
        return None


def write_ip(ip):
    try:
        with open(IP_FILE, "w") as f:
            f.write(ip)
    except:
        pass


async def check_ip_change():
    current_ip = get_public_ip()
    if not current_ip:
        return  # Don't send anything if IP fetch fails

    saved_ip = read_saved_ip()

    if saved_ip is None:
        write_ip(current_ip)
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(
                f"**Initial IP Detected:** `{current_ip}`\nSaved this IP for future comparison."
            )
        return

    if current_ip != saved_ip:
        write_ip(current_ip)
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(
                f"**IP Address changed:** `{saved_ip}` → `{current_ip}`"
            )


async def message_loop():
    global interval_seconds
    await bot.wait_until_ready()
    while running:
        await check_ip_change()
        await asyncio.sleep(interval_seconds)




# --- Commands ---

@bot.command(name="setinterval")
async def set_interval(ctx, seconds: int):
    global interval_seconds
    if seconds < MIN_INTERVAL_SECONDS or seconds > MAX_INTERVAL_SECONDS:
        await ctx.send(
            f"{ctx.author.mention} **Error:** Invalid interval.\n"
            f"- Minimum: `{MIN_INTERVAL_SECONDS}` seconds\n"
            f"- Maximum: `{MAX_INTERVAL_SECONDS}` seconds"
        )
        return

    interval_seconds = seconds
    await ctx.send(
        f"{ctx.author.mention} **Interval updated!**\n"
        f"New scan interval: `{interval_seconds}` seconds."
    )


@bot.command(name="settings")
async def show_settings(ctx):
    saved_ip = read_saved_ip() or "None (file missing)"
    await ctx.send(
        f"{ctx.author.mention} **Current Settings:**\n"
        f"- Monitoring: **Running**\n"
        f"- Saved IP: `{saved_ip}`\n"
        f"- Interval: `{interval_seconds}` seconds\n"
        f"- Channel ID: `{CHANNEL_ID}`"
    )


@bot.command(name="help")
async def help_command(ctx):
    await ctx.send(
        f"{ctx.author.mention} **IP Monitor Bot Commands:**\n\n"
        f"**!setinterval <seconds>**\n"
        f"• Changes how often the bot checks your public IP.\n"
        f"• Example: `!setinterval 3600` (checks every hour)\n\n"
        f"**!settings**\n"
        f"• Shows current monitoring settings.\n\n"
        f"**!help**\n"
        f"• Displays this help message.\n\n"
    )


# --- Startup Event ---

@bot.event
async def on_ready():
    # global current_user_mention
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print("Bot is ready!")

    channel = bot.get_channel(CHANNEL_ID)
    # current_user_mention = bot.user.mention

    if channel:
        await channel.send(
            f"✅ **IP Monitor Bot Online**\n"
            f"- Monitoring has started automatically.\n"
            f"- Current scan interval: `{interval_seconds}` seconds.\n"
            f"- Saved IP: `{read_saved_ip() or 'None (file missing)'}`"
        )
    else:
        print("Error: Could not find the target channel. Check the ID and permissions.")

    bot.loop.create_task(message_loop())


# --- Run the Bot ---
bot.run(BOT_TOKEN)