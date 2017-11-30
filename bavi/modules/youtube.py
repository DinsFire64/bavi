import logging
import re

log = logging.getLogger('bavi.modules.youtube')

YOUTUBE_REGEX = r""

compiled_yt_regex = re.compile(YOUTUBE_REGEX)

def init(bot):
    bot.add_command('yt', yt_search_command)
    bot.add_matcher(compiled_yt_regex, yt_search_command, priority='high')

def yt_search_command(bot, source, target, message, **kwargs):
    log.debug('youtube module triggered on: ' + message)
