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

# άλλες εντολές ή imports που έχεις πάνω...

@bot.command()
async def ticket(ctx):
    embed = discord.Embed(title="🎫 Υποστήριξη Voodoo OfficialV2", description="Παρακαλώ επιλέξτε τον λόγο που θέλετε να ανοίξετε ticket.", color=discord.Color.red())
    await ctx.send(embed=embed, view=TicketView())

bot.run("TOKEN_ΕΔΩ")  # αυτό ΠΑΝΤΑ να είναι τελευταίο!

# === 🎫 ΕΝΤΟΛΗ TICKET ===
from discord.ui import View, Select, Button
import asyncio

# IDs ρόλων που θα βλέπουν τα ticket (βάλε τα δικά σου)
STAFF_ROLES = [123456789012345678, 987654321098765432]

# Ρυθμίσεις εμφάνισης
EMBED_COLOR = discord.Color.red()
THUMBNAIL_URL = "https://www.leitwerk.de/media/e3/6a/d3/1706205188/massive.jpg"
EMBED_TITLE = "🎫 Υποστήριξη Voodoo OfficialV2"
EMBED_DESCRIPTION = "Παρακαλώ επιλέξτε τον λόγο που θέλετε να ανοίξετε ticket."

# === 📩 MENU ΕΠΙΛΟΓΩΝ ===
class TicketSelect(Select):
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
            }
        )

        # ✅ Πρόσβαση σε staff ρόλους
        for role_id in STAFF_ROLES:
            role = guild.get_role(role_id)
            if role:
                await ticket_channel.set_permissions(role, view_channel=True, send_messages=True)

        embed = discord.Embed(
            title=f"{EMBED_TITLE} - {self.values[0]}",
            description=(
                f"👋 Γεια σου {interaction.user.mention}!\n"
                "Παρακαλώ περιμένετε το **Staff Team** να σας εξυπηρετήσει.\n\n"
                "Αν θέλετε να **κλείσετε το ticket**, πατήστε το κουμπί παρακάτω 🔒"
            ),
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=f"{interaction.user.name} | Ticket System", icon_url=interaction.user.display_avatar.url)

        delete_button = Button(label="⛔ Κλείσιμο Ticket", style=discord.ButtonStyle.red)

        async def delete_callback(interact):
            await interact.response.send_message("⏳ Το ticket θα διαγραφεί σε 10 δευτερόλεπτα...", ephemeral=True)
            await asyncio.sleep(10)
            await ticket_channel.delete()

        delete_button.callback = delete_callback

        view = View()
        view.add_item(delete_button)

        await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(f"🎫 Δημιουργήθηκε ticket: {ticket_channel.mention}", ephemeral=True)

# === 📬 VIEW ΓΙΑ ΤΗΝ ΕΝΤΟΛΗ ===
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# === 🧠 ΕΝΤΟΛΗ !ticket ===
@bot.command()
async def ticket(ctx):
    embed = discord.Embed(title=EMBED_TITLE, description=EMBED_DESCRIPTION, color=EMBED_COLOR)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    await ctx.send(embed=embed, view=TicketView())
