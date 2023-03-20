import os
import marvelbot
import discord
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

@client.event
async def on_message(message):
    bot_command = message.content.lower()
    author = message.author
    if bot_command.startswith('/marvelbot'):
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
        creator_name, creator_comics, creator_pic_link = creator_info

        embed = discord.Embed(title=creator_name, description=f"Was involved in {creator_comics} comics.", color=0x109319)
        embed.set_author(name=author.display_name, icon_url=author.avatar)
        embed.set_footer(text="Data provided by Marvel. © 2023 MARVEL")
        if not creator_pic_link.split("/")[-1].startswith('image_not'):
            embed.set_thumbnail(url=creator_pic_link)

        await message.channel.send(embed=embed)

    if bot_command.startswith('lookup event'):
        event = bot_command.split('lookup event')[1].strip()
        event_info = marvelbot.event_search(event)
        event_name, event_desc, event_characters, event_creators, event_before, event_next, event_pic_link = event_info

        embed = discord.Embed(title=event_name, description=event_desc, color=0x109319)
        embed.set_author(name=author.display_name, icon_url=author.avatar)
        embed.add_field(name="Writers", value=f"{', '.join(event_creators)}", inline=False)
        embed.add_field(name="Characters Involved", value=f"{', '.join(event_characters)}", inline=True)
        embed.add_field(name="Before/After", value=f"Event Before: {event_before}\nEvent After: {event_next}", inline=True)
        embed.set_footer(text="Data provided by Marvel. © 2023 MARVEL")
        if not event_pic_link.split("/")[-1].startswith('image_not'):
            embed.set_thumbnail(url=event_pic_link)

        await message.channel.send(embed=embed)

client.run(DISCORD_TOKEN)
