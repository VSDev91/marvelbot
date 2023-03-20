import os
import requests
import hashlib
import datetime
from collections import Counter
from dotenv import load_dotenv
from itertools import chain

load_dotenv()

timestamp = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')
priv_key = os.getenv("priv_key")
pub_key = os.getenv("pub_key")

def hash_params():
    """ Marvel API requires server side API calls to include
    md5 hash of timestamp + public key + private key """

    hash_md5 = hashlib.md5()
    hash_md5.update(f'{timestamp}{priv_key}{pub_key}'.encode('utf-8'))
    hashed_params = hash_md5.hexdigest()

    return hashed_params


def character_search(character):
    params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 'nameStartsWith': character, "limit": "100"};
    response = requests.get('https://gateway.marvel.com:443/v1/public/characters',
                            params=params)
    data = response.json()
    try:
        character_profiles = [x['name'] for x in data['data']['results']]
        character_profile = data['data']['results'][0]
    except IndexError:
        all_responses = attempt_search(character)
        return all_responses
    else:
        char_id = character_profile['id']
        char_name = character_profile['name']
        char_desc = character_profile['description']
        img_link = character_profile['thumbnail']
        img_link = f"{img_link['path']}.{img_link['extension']}"
        char_events, related_chars = character_events(char_id)

    return char_name, char_desc, character_profiles, char_events, related_chars, img_link


def related_characters(events):
    characters = [char['name'] for event in events for char in event['characters']['items']]
    counts = Counter(characters)
    most_common_chars = counts.most_common(5)
    most_common_chars = [x for x, y in most_common_chars]
    return most_common_chars


def attempt_search(character):
    all_responses = []
    terms_to_search = character.split()
    for term in terms_to_search:
        cleaned_term = [char for char in term if char.isalpha()]
        cleaned_term = ''.join(cleaned_term)
        params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 'nameStartsWith': cleaned_term};
        response = requests.get('https://gateway.marvel.com:443/v1/public/characters',
                                params=params)
        data = response.json()
        term_response = [x['name'] for x in data['data']['results']]
        all_responses.append([x for x in term_response if len(term_response) > 0])
    responses = ', '.join(list(chain.from_iterable(all_responses)))
    return responses


def creator_search(character):
    params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 'nameStartsWith': character};
    response = requests.get('https://gateway.marvel.com:443/v1/public/creators',
                            params=params)
    data = response.json()
    creator_profile = data['data']['results'][0]
    creator_name = creator_profile['fullName']
    creator_comics = creator_profile['comics']['available']
    img_link = creator_profile['thumbnail']
    img_link = f"{img_link['path']}.{img_link['extension']}"

    return creator_name, creator_comics, img_link


def event_search(character):
    params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 'nameStartsWith': character};
    response = requests.get('https://gateway.marvel.com:443/v1/public/events',
                            params=params)
    data = response.json()
    event_profile = data['data']['results'][0]
    event_name = event_profile['title']
    event_desc = event_profile['description']
    img_link = event_profile['thumbnail']
    img_link = f"{img_link['path']}.{img_link['extension']}"
    event_characters = [x['name'] for x in event_profile['characters']['items']]
    event_creators = [x['name'] for x in event_profile['creators']['items'] if x['role'] == 'writer']
    event_next = event_profile['next']['name']
    event_before = event_profile['previous']['name']
    return event_name, event_desc, event_characters, event_creators, event_before, event_next, img_link


def character_events(char_id):
    params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), "limit": 100};
    response = requests.get(f'https://gateway.marvel.com:443/v1/public/characters/{char_id}/events',
                            params=params)
    data = response.json()
    char_events = [x['title'] for x in data['data']['results']]
    related_chars = related_characters(data['data']['results'])
    return char_events, related_chars
