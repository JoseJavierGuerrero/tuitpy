#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2011 Alejandro Gómez <alejandroogomez@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A Python script for using Twitter from the command line."""

__author__ = 'alejandroogomez@gmail.com'
__version__ = '0.1'

import inspect
import sys

try:
    import twitter
except ImportError:
    print 'Unable to find twitter-py library'

# INSERT YOUR TOKENS HERE:
# Twitter specific constants
_CONSUMER_KEY = ''
_CONSUMER_SECRET = ''
_ACCES_TOKEN_KEY = ''
_ACCES_TOKEN_SECRET = ''
_USERNAME = ''                  # don`t include the @, just your user name

# Local constants
_MAX_ARGS = 4
    
def tweet(text=None):
    """
    Tweets the specified text from the authenticated user.
    
    Args:
        text    
            The text of the tweet.
    """
    if text is not None:
        text = str(text)
        textLength = len(text)
        if textLength > twitter.CHARACTER_LIMIT:
            print 'Your tweet is %d characters' % textLength
            return
        status = api.PostUpdate(text)
        print 'Tweet sent!'
        print formatTweet(status)
    else:
        print 'Usage: %s -t tweet' % sys.argv[0]
    
def sendMessage(user=None, text=None):
    """
    Sends text as a Direct Message to user.
    
    Args:
        user
            The ID or screen name of the recipient user.
        text
            The message text to be posted.
    """
    if user and text:
        user = str(user)
        text = str(text)
        textLength = len(text)
        if textLength > twitter.CHARACTER_LIMIT:
            print 'Your message is %d characters' % textLength
            return
        try:
            status = api.PostDirectMessage(user, text)
        except twitter.TwitterError:
            print 'Error! Message not sent!'
            print 'Are you sure that %s is a valid username or ID?' % user
        else:
            print 'Message sent!'
            print formatMessage(status)
    else:
        print 'Usage: %s -dm user text' % sys.argv[0]
    
def timeline(count=20):
    """
    Shows the last count tweets in your TL if it's specified. 
    The last 20 tweets if not.
    
    Args:
        count   
            Number of tweets to be displayed.
            Maximum 20.
    """
    try:
        count = int(count)
        timeline = api.GetFriendsTimeline(_USERNAME, count)
    except ValueError:
        print 'Usage: %s -tl [count]' % sys.argv[0]
    except twitter.TwitterError:
        print 'There is a problem with Twitter'
    else:
        timeline.reverse()
        print '\n\n'.join([formatTweet(tweet) for tweet in timeline])
    
def mentions(count=20):
    """
    Shows the last count mentions if it's specified. 
    The last 20 mentions if not.
    
    Args:
        count   
            Number of tweets to be displayed.
            Maximum 20.
    """
    mentions = api.GetMentions()
    try:
        count = int(count)
    except ValueError:
        print 'Usage: %s -m [count]' % sys.argv[0]
    else:
        mentions = mentions[:count]
        mentions.reverse()
        print '\n\n'.join([formatTweet(tweet) for tweet in mentions])   
    
def getMessages(count=20):
    """
    Shows the last count messages if it's specified. 
    The last 20 messages if not.

    Args:
        count   
            Number of messages to be displayed.
            Maximum 20.
    """
    directMessages = api.GetDirectMessages()
    try:
        count = int(count)
    except ValueError:
        print 'Usage: %s -gm [count]' % sys.argv[0]
    else:
        directMessages = directMessages[:count]
        directMessages.reverse()
        print '\n\n'.join([formatMessage(dm) for dm in directMessages])

def favorites(count=20, user=None):
    """
    Shows the last count favorites for user if it's specified. 
    The last count favorites of authenticated user if not.
    
    Args:
        count   
            Number of tweets to be displayed.
            Maximum 20.
        user
            The ID or screen name of user whom favorites are fetched.
    """
    try:
        count = int(count)
        if user is None:
            favorites = api.GetFavorites()
        else:
            favorites = api.GetFavorites(str(user))
    except ValueError:
        print 'Usage: %s -f [count, [user]]' % sys.argv[0]
    except twitter.TwitterError:
        print 'There is a problem with Twitter'
    else:
        favorites = favorites[:count]
        favorites.reverse()
        print '\n\n'.join([formatTweet(tweet) for tweet in favorites])
    
def formatTweet(status):
    user = status.user
    name = '@%s' % user.GetScreenName()
    date = '\t\t%s' % status.GetCreatedAt()
    text = '\t%s' % status.GetText()
    return '\n'.join([name + date, text])
    
def formatMessage(status):
    sender = '@%s' % status.GetSenderScreenName()
    recipient = '@%s' % status.GetRecipientScreenName()
    text = '\t%s' % status.GetText()
    return '\n'.join([sender + ' -> ' + recipient, text])
    
def help():
    _flags =    [
                '-dm user text \n\tSend text as a DM to @user.',
                '-tl [count] \n\tShow count tweets of your TL.',
                '-m [count] \n\tShow count mentions.',
                '-t text \n\tTweet text.',
                '-gm [count] \n\tShow count last DMs.',
                '-f [count [user]] \n\tShow your last count favorites or user\'s'
                ]
    print 'Usage: %s flag [args]' % sys.argv[0]
    print
    print 'flag [args]:'
    print '\n'.join(['  ' + flag for flag in _flags])
    
# Dict with following format:
# flag: function
_ARGS = {
        '-help': help,
        '-dm': sendMessage,
        '-tl': timeline,
        '-m': mentions,
        '-t': tweet,
        '-gm': getMessages,
        '-f': favorites
        }

if __name__ == '__main__':
    api = twitter.Api(  _CONSUMER_KEY, _CONSUMER_SECRET,
                        _ACCES_TOKEN_KEY, _ACCES_TOKEN_SECRET)
    argc = len(sys.argv)
    if argc == 1 or argc > _MAX_ARGS or sys.argv[1] is '-help':
        help()
    else:
        try:            
            # Take arg number and default arg number in function
            function = _ARGS[sys.argv[1]]
            argspec = inspect.getargspec(function)
            args_num = len(argspec.args)
            default_args = 0
            if argspec.defaults is not None:
                default_args = len(argspec.defaults)
            
            def validArgNumber(args_):
                sameArgNumber = args_ == args_num
                mandatoryArgs = args_num - default_args
                notFew = sameArgNumber or args_ >= mandatoryArgs 
                notTooMuch = args_ <= args_num
                return notFew and notTooMuch
            
            # Call the corresponding function
            function_args = argc - 2
            if function_args == 2 and validArgNumber(2):
                function(sys.argv[2], sys.argv[3])
            elif function_args == 1 and validArgNumber(1):
                function(sys.argv[2])
            elif function_args == 0 and validArgNumber(0):
                function()
            else:
                help()
        except KeyError:
            help()