import logging
import re
import requests
import json
import dateutil.parser

log = logging.getLogger('bavi.modules.youtube')

YOUTUBE_REGEX = r"(?:youtube(?:-nocookie)?\.com/(?:[^/]+/./|(?:v|e(?:mbed)?)/|.*?[?&]v=)|youtu\.be/)([^\"&?/ ]{11})"

DURATION_REGEX = r"PT(\d+H)?(\d+M)?(\d+S)?"

YT_BASE_API = "https://www.googleapis.com/youtube/v3/"

STRING_FORMAT="[YouTube] {0} | Uploader: {1} | Uploaded: {2} | Length: {3} | Views: {4} | Comments: {5} | \x0303{6}+\x03 | \x0304{7}-\x03"

compiled_yt_regex = re.compile(YOUTUBE_REGEX)
compiled_duration_regex = re.compile(DURATION_REGEX)

def init(bot):
    bot.add_command('yt', yt_search_command)
    bot.add_command('youtube', yt_search_command)
    bot.add_matcher(compiled_yt_regex, yt_search_command, priority='high')
    
def yt_search_command(bot, source, target, message, **kwargs):
    log.debug('youtube search module triggered on: ' + message)
    
    try:
        #If there is a regex match, then pull video IDs
        #If no match, then run a youtube search.
        if 'match' in kwargs:
            all_ids = compiled_yt_regex.findall(message)
            
            for video_id in all_ids:
                bot.say(target, get_yt_video_info(bot.config['youtube'].get('key'), video_id))
        else :
            bot.say(target, yt_search(bot.config['youtube'].get('key'), message))
    except Exception as e:
        exception_msg = type(e).__name__ + ': ' + str(e)
        log.exception('Error retrieving YouTube information: %s', exception_msg)
        bot.say(target, exception_msg)
        
def video_info_to_string(video_info):
    
    title = video_info['snippet']['title']
    uploader = video_info['snippet']['channelTitle']
    views = human_readable(video_info['statistics']['viewCount'])
    comments = human_readable(video_info['statistics']['commentCount'])
    like_count = human_readable(video_info['statistics']['likeCount'])
    dislike_count = human_readable(video_info['statistics']['dislikeCount'])
    
    uploadDate = dateutil.parser.parse(video_info['snippet']['publishedAt']).date()
    length = parse_iso8601_duration(video_info['contentDetails']['duration'])

    return STRING_FORMAT.format(title, uploader, uploadDate, length, views, comments, like_count, dislike_count)
    
def parse_iso8601_duration(iso8601_duration):
    match = compiled_duration_regex.match(iso8601_duration).groups()
    result = ""
    
    hours = int(match[0][:-1]) if match[0] else 0
    mins = int(match[1][:-1]) if match[1] else 0
    secs = int(match[2][:-1]) if match[2] else 0
    
    result += str(hours) + "h " if hours > 0 else ""
    result += str(mins) + "m " if mins > 0 else ""
    result += str(secs) + "s" if secs > 0 else ""
    
    return result
    
def human_readable(number):
    suffixes = ['', 'K', 'M', 'B', 'T']
    
    i = 0
    number = float(number)
    
    while i < len(suffixes) and number > 1000:
        number /= 1000
        i += 1

    return str(round(number, 1)).rstrip('.0') + suffixes[i]
    
def check_yt_response(json_response):
    if 'error' in json_response:
        message = "Error " + str(json_response['error']['code']) + ": " + json_response['error']['message']
    
        if json_response['error']['errors'][0]:
            message += " Reason: " + json_response['error']['errors'][0]['reason']
        
        raise Exception(message)
    
def get_yt_video_info(api_key, video_id):

    url = YT_BASE_API + 'videos'
    
    kwargs = {}
    kwargs['part'] = "snippet,statistics,contentDetails"
    kwargs['id'] = video_id
    kwargs['key'] = api_key
    
    response = requests.get(url, params=kwargs)

    yt_response = response.json()
    
    check_yt_response(yt_response)

    return video_info_to_string(yt_response['items'][0])
    
def yt_search(api_key, search_string):
    
    url = YT_BASE_API + 'search'
    
    kwargs = {}
    kwargs['key'] = api_key
    kwargs['part'] = "snippet"
    kwargs['maxResults'] = 1
    kwargs['q'] = search_string

    response = requests.get(url, params=kwargs)
    yt_response = response.json()
    
    check_yt_response(yt_response)
    
    return get_yt_video_info(api_key, yt_response['items'][0]['id']['videoId'])
