#!/bin/env python
import requests
import json
import appdirs
import configparser
import os
import sys

APP_NAME = 'youtube-playlist-backup'
CONFIG_NAME = 'config.ini'
DEFAULT_CONFIG = '[youtube]\n#api_key=\n#channel_id=\n'

def add_opt_param(params, key, value):
    if not (value is None):
        params[key] = value

def add_api_key(params, api_key):
    add_opt_param(params, 'key', api_key)

def youtube_api_url(sub_api):
    return 'https://www.googleapis.com/youtube/v3/' + sub_api

def request_template(params, page_token, api_key, youtube_api_part):
    add_api_key(params, api_key)
    add_opt_param(params, 'pageToken', page_token)
    r = requests.get(youtube_api_url(youtube_api_part), params = params)
    r.raise_for_status()
    return r

def request_playlists(channel_id, page_token = None, api_key = None):
    params = { 'maxResults' : '50'
             , 'channelId' : channel_id
             , 'part' : 'snippet'
             , 'fields' : 'items(id,snippet/title),nextPageToken'
             }
    return request_template(params, page_token, api_key, 'playlists')

# TODO parse all playlists at once with the id property
def request_playlist_items(playlist_id, page_token = None, api_key = None):
    params = { 'maxResults' : '50'
             , 'playlistId' : playlist_id
             , 'part' : 'snippet'
             , 'fields' : 'items/snippet(title,resourceId/videoId),nextPageToken'
             }
    return request_template(params, page_token, api_key, 'playlistItems')

def parse_json_playlists(json):
    return [(i['snippet']['title'], i['id']) for i in json['items']]

def parse_json_playlist_items(json):
    snippets = map(lambda i: i['snippet'], json['items'])
    return [(s['title'], s['resourceId']['videoId']) for s in snippets]

# Make json requests for all available pages and merge the results such that
# everything is fetched.
def get_template(request, parse):
    next_page = None
    while True:
        json = request(next_page).json()
        yield parse(json)
        if 'nextPageToken' in json:
            next_page = json['nextPageToken']
        else:
            break

def get_playlists(channel_id, api_key):
    return get_template(lambda np: request_playlists(channel_id, np, api_key), parse_json_playlists)

def get_playlist_items(playlist_id, api_key):
    return get_template(lambda np: request_playlist_items(playlist_id, np, api_key), parse_json_playlist_items)

def get_all(channel_id, api_key):
    for (playlist_title, playlist_id) in get_playlists(channel_id, api_key):
        yield (playlist_title, get_playlist_items(playlist_id, api_key))

def print_all(channel_id, api_key):
    for (playlist_title, playlist_items) in get_all(channel_id, api_key):
        print('')
        print(playlist_title)
        print('')
        for (item_title, video_id) in playlist_items:
            print(item_title, '-', "https://youtube.com/watch?v={}".format(video_id))

def print_usage():
    print('Usage:\n\n    {} CHANNEL_ID\n'.format(APP_NAME))

def fail():
    print_usage()
    sys.exit(1)

def parse_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    youtube_section = config['youtube']
    return (youtube_section.get('api_key'), youtube_section.get('channel_id'))

if __name__ == '__main__':
    num_args = len(sys.argv)
    if num_args > 2:
        fail()
    else:
        api_key = None
        channel_id = None
        config_base_path = appdirs.user_config_dir(APP_NAME)
        config_path = os.path.join(config_base_path, CONFIG_NAME)

        if os.path.exists(config_path):
            (api_key, channel_id) = parse_config(config_path)
        else:
            print('Creating empty configuration file:', config_path)
            if not os.path.exists(config_base_path):
                os.mkdir(config_base_path)
            with open(config_path, 'x') as config_file:
                config_file.write(DEFAULT_CONFIG)
        if num_args == 2:
            channel_id = sys.argv[1]

        if channel_id is None:
            fail()
        else:
            print_all(channel_id, api_key)
