#!/bin/env python
import requests
import json

# An api key is not strictly necessary. However note that there is an upper
# limit on how much requests you can make without one.
API_KEY = None

# The id of the channel you want to dump.
CHANNEL_ID = None

def add_opt_param(params, key, value):
    if not (value is None):
        params[key] = value

def add_api_key(params):
    add_opt_param(params, 'key', API_KEY)

def youtube_api_url(sub_api):
    return 'https://www.googleapis.com/youtube/v3/' + sub_api

def request_template(params, page_token, youtube_api_part):
    add_api_key(params)
    add_opt_param(params, 'pageToken', page_token)
    r = requests.get(youtube_api_url(youtube_api_part), params = params)
    r.raise_for_status()
    return r

def request_playlists(channel_id, page_token = None):
    params = { 'maxResults' : '50'
             , 'channelId' : channel_id
             , 'part' : 'snippet'
             , 'fields' : 'items(id,snippet/title)'
             }
    return request_template(params, page_token, 'playlists')

# TODO parse all playlists at once with the id property
def request_playlist_items(playlist_id, page_token = None):
    params = { 'maxResults' : '50'
             , 'playlistId' : playlist_id
             , 'part' : 'snippet'
             , 'fields' : 'items/snippet(title,resourceId/videoId)'
             }
    return request_template(params, page_token, 'playlistItems')

def parse_json_playlists(json):
    return [(i['snippet']['title'], i['id']) for i in json['items']]

def parse_json_playlist_items(json):
    snippets = map(lambda i: i['snippet'], json['items'])
    return [(s['title'], s['resourceId']['videoId']) for s in snippets]

# Make json requests for all available pages and merge the results such that
# everything is fetched.
def get_template(request, parse):
    result = []
    next_page = None
    while True:
        json = request(next_page).json()
        result += parse(json)
        if 'nextPageToken' in json:
            next_page = json['nextPageToken']
        else:
            break
    return result

def get_playlists(channel_id):
    return get_template(lambda np: request_playlists(channel_id, np), parse_json_playlists)

def get_playlist_items(playlist_id):
    return get_template(lambda np: request_playlist_items(playlist_id, np), parse_json_playlist_items)

if __name__ == '__main__':
    result = []
    for (playlist_title, playlist_id) in get_playlists(CHANNEL_ID):
        result.append((playlist_title, get_playlist_items(playlist_id)))

    for (playlist_title, playlist_items) in result:
        print('')
        print(playlist_title)
        print('')
        for (item_title, video_id) in playlist_items:
            print(item_title, '-', "https://youtube.com/watch?v={}".format(video_id))
