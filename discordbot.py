import os
import marvelbot
import discord
import io
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_2")
intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Currently connected to the below servers:\n')
    for guild in client.guilds:
        print(f"Text Channels accessible in {guild} : {guild.id}")
        # for channel in guild.text_channels:
        #     print(f"{channel} : {channel.id}")

@client.event
async def on_message(message):
    bot_command = message.content.lower()

    if bot_command.startswith('marvelbot help'):
        await message.channel.send(
            f'Commands to Use:\n' \
            f'Lookup a Character or Hero: type "lookup character TYPE_CHAR_HERE"\n' \
            f'Lookup a Creator: type "lookup creator TYPE_CREATOR_HERE"\n' \
            f'Lookup an Event: type "lookup event TYPE_EVENT_HERE"\n' \
            f'Below is an example character search.\n\n'
        )
        await message.channel.send(
            f"lookup character iron man\n\n"
        )

    if bot_command.startswith('lookup character'):
        character = bot_command.split('lookup character')[1].strip()
        author = message.author
        await message.channel.send(f'Retrieving result(s) for {character.capitalize()}')
        try:
            character_info = marvelbot.character_search(character)
            char_name, char_desc, char_profiles, char_events, related_chars, char_img = character_info
        except (KeyError, TypeError, ValueError) as e:
            with open('log_file.txt', 'a') as file:
                file.write(f"Term Searched: {character}\n{e}\n\n")
            await message.channel.send(f'Unable to find anything starting with that, try again.\n\n'
                                       f"Maybe try a term below:\n"\
                                       f"{character_info}")
            return
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(char_img) as resp:
                    if resp.status != 200:
                        return await channel.send('Could not download file...')
                    data = io.BytesIO(await resp.read())
            if len(char_profiles) == 1:
                char_profiles = ''
            embed = discord.Embed(title=char_name, description=char_desc, color=0x109319)
            embed.set_author(name=author.display_name, icon_url=author.avatar)
            embed.add_field(name="Events In", value=f"{', '.join(char_events)}", inline=False)
            embed.add_field(name="Commonly With", value=f"{', '.join(related_chars)}", inline=True)
            embed.add_field(name="Similarly Named", value=f"{', '.join(char_profiles[1:])}", inline=True)
            embed.set_footer(text="Data provided by Marvel. © 2023 MARVEL")
            if not char_img.split("/")[-1].startswith('image_not'):
                embed.set_thumbnail(url=char_img)
            await message.channel.send(embed=embed)

    if bot_command.startswith('lookup creator'):
        creator = bot_command.split('lookup creator')[1].strip()
        creator_info = marvelbot.creator_search(creator)
        creator_name, creator_comics = creator_info
        await message.channel.send(f'Name: {creator_name}\nDescription: Was involved in the creation of {creator_comics} comics.')

    if bot_command.startswith('lookup event'):
        event = bot_command.split('lookup event')[1].strip()
        event_info = marvelbot.event_search(event)
        event_name, event_desc, event_start, event_end, event_characters, event_creators, event_before, event_next = event_info
        await message.channel.send(
            f"Event: {event_name}\n" \
            f"Description: {event_desc}\n\n" \
            f"Event Span: From {event_start} to {event_end}\n" \
            f"Prior Event: {event_before}\n" \
            f"Next Event: {event_next}\n\n" \
            f"Characters Involved: {', '.join(event_characters)}\n\n" \
            f"Writers: {', '.join(event_creators)}\n"
            )

client.run(DISCORD_TOKEN)
