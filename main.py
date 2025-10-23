import discord
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == "ping":
        await message.channel.send("Pong!")

TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)

# ======================  TICKET SYSTEM ======================
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio

# Δημιουργούμε νέο bot αντικείμενο για commands (ώστε να λειτουργεί η εντολή !ticket)
bot = commands.Bot(command_prefix="!", intents=intents)

# === ΒΑΛΕ ΕΔΩ ΤΑ ROLE IDs ΠΟΥ ΘΑ ΒΛΕΠΟΥΝ ΤΑ TICKET ===
STAFF_ROLES = [1288087153997516913, 1289538235495878659, 1288090189255675944, 1288106262126657586]  # 👈 άλλαξέ τα με τα δικά σου role IDs

# === ΡΥΘΜΙΣΕΙΣ EMBED ===
EMBED_COLOR = discord.Color.red()
EMBED_TITLE = "🎫 Υποστήριξη Voodoo OfficialV2"
EMBED_DESCRIPTION = "Παρακαλώ επιλέξτε τον λόγο που θέλετε να ανοίξετε ticket."

# === ΟΤΑΝ ΤΟ BOT ΕΙΝΑΙ ΕΤΟΙΜΟ ===
@bot.event
async def on_ready():
    print(f"✅ Ticket System έτοιμο ως {bot.user}")

# === ΕΝΤΟΛΗ !ticket ===
@bot.command()
async def ticket(ctx):
    class TicketSelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="👑 Owner Support", description="Επικοινωνία με Owner"),
                discord.SelectOption(label="📞 General Support", description="Βοήθεια από Staff"),
                discord.SelectOption(label="🚫 Ban Appeal", description="Αίτηση για unban"),
                discord.SelectOption(label="💼 Job Application", description="Αίτηση για δουλειά"),
                discord.SelectOption(label="🚩 Report Player", description="Αναφορά παίκτη"),
            ]
            super().__init__(placeholder="📩 Επιλέξτε λόγο για ticket...", options=options)

        async def callback(self, interaction: discord.Interaction):
            guild = interaction.guild
            category = discord.utils.get(guild.categories, name="🎫 Tickets")
            if category is None:
                category = await guild.create_category("🎫 Tickets")

            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=category,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(view_channel=True),
                },
            )

            # ✅ ΔΩΣΕ ΠΡΟΣΒΑΣΗ ΣΕ OWNER/STAFF ROLES
            for role_id in STAFF_ROLES:
                role = guild.get_role(role_id)
                if role:
                    await ticket_channel.set_permissions(role, view_channel=True, send_messages=True)

            embed = discord.Embed(
                title=f"🎟️ Ticket - {self.values[0]}",
                description="👋 Καλησπέρα! Ένα μέλος του Staff θα σας εξυπηρετήσει σύντομα.\n\nΑν θέλετε να κλείσετε το ticket, πατήστε 🔒",
                color=EMBED_COLOR
            )
            embed.set_footer(text=f"{interaction.user.name} | Ticket System")

            delete_button = Button(label="🔒 Κλείσιμο Ticket", style=discord.ButtonStyle.red)

            async def delete_callback(interact):
                await interact.response.send_message("⏳ Το ticket θα διαγραφεί σε 10 δευτερόλεπτα...", ephemeral=True)
                await asyncio.sleep(10)
                await ticket_channel.delete()

            delete_button.callback = delete_callback

            view = View()
            view.add_item(delete_button)

            await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
            await interaction.response.send_message(f"✅ Το ticket δημιουργήθηκε: {ticket_channel.mention}", ephemeral=True)

    class TicketView(View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(TicketSelect())

    embed = discord.Embed(title=EMBED_TITLE, description=EMBED_DESCRIPTION, color=EMBED_COLOR)
    await ctx.send(embed=embed, view=TicketView())

# === ΤΡΕΧΟΥΜΕ ΚΑΙ ΤΑ ΔΥΟ ΜΑΖΙ (client + bot)
import threading

def run_ticket():
    bot.run(os.getenv("DISCORD_TOKEN"))

threading.Thread(target=run_ticket).start()
