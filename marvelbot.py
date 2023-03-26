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
        return retrieve_all(character, 'nameStartsWith', 'characters', 'name')
    else:
        char_id = character_profile['id']
        char_name = character_profile['name']
        char_desc = character_profile['description']
        img_link = character_profile['thumbnail']
        char_events, related_chars = character_events(char_id)

    return char_name, char_desc, character_profiles, char_events, related_chars, img_link


def character_events(char_id):
    params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), "limit": 100};
    response = requests.get(f'https://gateway.marvel.com:443/v1/public/characters/{char_id}/events',
                            params=params)
    data = response.json()

    char_events = [x['title'] for x in data['data']['results']]
    related_chars = related_characters(data['data']['results'])

    return char_events, related_chars


def related_characters(events):
    characters = [char['name'] for event in events for char in event['characters']['items']]
    counts = Counter(characters)
    most_common_chars = counts.most_common(5)
    most_common_chars = [x for x, y in most_common_chars]
    return most_common_chars


def creator_search(character):
    params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 'nameStartsWith': character};
    response = requests.get('https://gateway.marvel.com:443/v1/public/creators',
                            params=params)
    data = response.json()

    creator_profile = data['data']['results'][0]
    creator_name = creator_profile['fullName']
    creator_comics = creator_profile['comics']['available']
    img_link = creator_profile['thumbnail']

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
    event_next = event_profile['next']['name']
    event_before = event_profile['previous']['name']
    event_characters = [x['name'] for x in event_profile['characters']['items']]
    event_creators = [x['name'] for x in event_profile['creators']['items'] if x['role'] == 'writer']

    return event_name, event_desc, event_characters, event_creators, event_before, event_next, img_link

def comic_search(comic):
    return retrieve_all(comic, 'titleStartsWith', 'comics', 'title')
    # params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 'titleStartsWith': comic, "limit": "100"};
    # response = requests.get('https://gateway.marvel.com:443/v1/public/comics',
    #                         params=params)
    # data = response.json()
    # try:
    #     comic_profile = data['data']['results'][0]
    # except IndexError:
    # else:
    #     comic_id = comic_profile['id']
    #     comic_title = comic_profile['title']
    #     comic_desc = comic_profile['description']
    #     comic_series = comic_profile['series']['name']
    #     comic_series_id = comic_profile['series']['resourceURI'].split('1')[-1]
    #     comic_creators = [x['name'] for x in comic_profile['creators']['items'] if x['role'] == 'writer']
    #     comic_char = [x['name'] for x in comic_profile['characters']['items']]
    #     comic_img = comic_profile['thumbnail']
    # fetch back using comic_series_id to pull back series info
    # return comic_title, comic_desc, comic_series, comic_creators, comic_char, comic_img

def series_search(series):
    return retrieve_all(series, 'titleStartsWith', 'series', 'title' )
#     params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 'titleStartsWith': series, "limit": "100"};
#     response = requests.get('https://gateway.marvel.com:443/v1/public/series',
#                             params=params)
#     data = response.json()
#
#     series_profile = data['data']['results'][0]
#     id = series_profile['id']
#     title = series_profile['title']
#     desc = series_profile['description']
#     creators = [x['name'] for x in series_profile['creators']['items'] if x['role'] == 'writer']
#     chars = [x['name'] for x in series_profile['characters']['items']]
#     comics = [x['name'] for x in series_profile['comics']['items']]
#     img_link = series_profile['thumbnail']
#     next = series_profile['next']
#     before = series_profile['previous']
# # aggregate all possible series
#     return title, desc, creators, chars, comics, img_link, next, before


def retrieve_all(term_to_search, param_filter, url, loop_var):
    all_responses = []
    terms_to_search = term_to_search.split()
    for term in terms_to_search:
        cleaned_term = ''.join([char for char in term if char.isalpha()])
        params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), param_filter: cleaned_term};
        response = requests.get(f'https://gateway.marvel.com:443/v1/public/{url}',
                                params=params)
        data = response.json()
        term_response = [x[loop_var] for x in data['data']['results']]
        all_responses.append([x for x in term_response if len(term_response) > 0])
    responses = ', '.join(list(chain.from_iterable(all_responses)))
    return responses