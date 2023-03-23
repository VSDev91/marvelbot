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
            char_name, char_desc, char_profiles, char_events, related_chars, img_link = character_info
        except (KeyError, TypeError, ValueError, IndexError) as e:
            await error_logging(character, e, message)
            if character_info:
                await message.channel.send(f"Try {character_info}")
        else:
            embed = discord.Embed(title=char_name, description=char_desc, color=0x109319)
            embed.add_field(name="Events In", value=f"{', '.join(char_events)}", inline=False)
            embed.add_field(name="Commonly With", value=f"{', '.join(related_chars)}", inline=True)
            embed.add_field(name="Similarly Named", value=f"{', '.join(char_profiles[1:])}", inline=True)
            embed_img(img_link, embed, author)

            await message.channel.send(embed=embed)

    if bot_command.startswith('lookup creator'):
        creator = bot_command.split('lookup creator')[1].strip()
        try:
            creator_info = marvelbot.creator_search(creator)
            creator_name, creator_comics, img_link = creator_info
        except (KeyError, TypeError, ValueError, IndexError) as e:
            await error_logging(creator, e, message)
        else:
            embed = discord.Embed(title=creator_name, description=f"Was involved in {creator_comics} comics.", color=0x109319)
            embed_img(img_link, embed, author)

            await message.channel.send(embed=embed)

    if bot_command.startswith('lookup event'):
        event = bot_command.split('lookup event')[1].strip()
        try:
            event_info = marvelbot.event_search(event)
            event_name, event_desc, event_characters, event_creators, event_before, event_next, img_link = event_info
        except (KeyError, TypeError, ValueError, IndexError) as e:
            await error_logging(event, e, message)
        else:
            embed = discord.Embed(title=event_name, description=event_desc, color=0x109319)
            embed.add_field(name="Writers", value=f"{', '.join(event_creators)}", inline=False)
            embed.add_field(name="Characters Involved", value=f"{', '.join(event_characters)}", inline=True)
            embed.add_field(name="Before/After", value=f"Event Before: {event_before}\nEvent After: {event_next}", inline=True)
            embed_img(img_link, embed, author)

            await message.channel.send(embed=embed)


def embed_img(img_link, embed, author):
    img_link = f"{img_link['path']}.{img_link['extension']}"
    if not img_link.split("/")[-1].startswith('image_not'):
        embed.set_thumbnail(url=img_link)
    embed.set_author(name=author.display_name, icon_url=author.avatar)
    embed.set_footer(text="Data provided by Marvel. © 2023 MARVEL")


async def error_logging(term, e, message):
    with open('log_file.txt', 'a') as file:
        file.write(f"Term Searched: {term}\n{message.content}\n{e}\n\n")
    await message.channel.send(f'Unable to find anything starting with {term}, try again.')
    return

client.run(DISCORD_TOKEN)