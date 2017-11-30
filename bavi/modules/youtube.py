import logging
import re
import requests
import json

log = logging.getLogger('bavi.modules.youtube')

YOUTUBE_REGEX = r""

YT_BASE_API = 'https://www.googleapis.com/youtube/v3/'

compiled_yt_regex = re.compile(YOUTUBE_REGEX)

STRING_FORMAT='[YouTube] {0} | Uploader: {1} | Uploaded: {2} | Length: {3} | Views: {4} | Comments: {5} | {6}+ | {7}-'

def init(bot):
    bot.add_command('yt', yt_search_command)
    bot.add_matcher(compiled_yt_regex, yt_search_command, priority='high')

def yt_search_command(bot, source, target, message, **kwargs):
    log.debug('youtube module triggered on: ' + message)
    
    bot.say(target, yt_search(bot.config['youtube'].get('key'), message))
    
def return_formatted_video_info(video_info):
    
    title = video_info['snippet']['title']
    uploader = video_info['snippet']['channelTitle']
    uploadDate = video_info['snippet']['publishedAt']
    length = video_info['contentDetails']['duration']
    views = video_info['statistics']['viewCount']
    comments = video_info['statistics']['commentCount']
    like_count = video_info['statistics']['likeCount']
    dislike_count = video_info['statistics']['dislikeCount']

    
    return STRING_FORMAT.format(title, uploader, uploadDate, length, views, comments, like_count, dislike_count)
    
def get_yt_video_info(api_key, video_id):

    url = YT_BASE_API + 'videos'
    
    kwargs = {}
    kwargs['part'] = "snippet,statistics,contentDetails"
    kwargs['id'] = video_id
    kwargs['key'] = api_key
    
    response = requests.get(url, params=kwargs)
    
    yt_response = response.json()['items'][0]
    
    return return_formatted_video_info(yt_response)
    
def yt_search(api_key, search_string):
    
    url = YT_BASE_API + 'search'
    
    kwargs = {}
    kwargs['key'] = api_key
    kwargs['part'] = "snippet"
    kwargs['maxResults'] = 1
    kwargs['q'] = search_string

    response = requests.get(url, params=kwargs)
    returned_video_id = response.json()['items'][0]['id']['videoId']
    
    return get_yt_video_info(api_key, returned_video_id)
