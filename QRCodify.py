#!/usr/bin/python
import praw
import pdb
import re
import os
import datetime
import traceback
import pyqrcode
import unicodedata
from config_bot import *
from pprint import pprint
from collections import deque 
from time import sleep
from enum import Enum


CACHE_SIZE       = 200
SEARCH_TERM = re.compile('/u/%s\b' % REDDIT_USERNAME, re.I)
DATA_BLOCKS = {'10':'▀','01':'▄','11':'█','00':' '}


def main():
    # Check that the file that contains our username exists
    if not os.path.isfile("config_bot.py"):
        print("You must create a config file with your username and password.")
        exit(1)

    print('QRCodify Reddit bot')

    current_sub = ''

    # Create the Reddit instance
    user_agent = ("Automated comment for /u/"+REDDIT_USERNAME)
    r = praw.Reddit(user_agent=user_agent)
    # and login
    r.login(REDDIT_USERNAME, REDDIT_PASS)

    cache = deque(maxlen=CACHE_SIZE) # double-ended queue
    sub_wait = {} # rate limit wait times for subreddits
    already_done = set()

    running = True
    while running:    
        try:
            mentions = r.get_unread()

            #Check new mentions
            for m in mentions:
                if m.id in cache:
                    continue
                if m.subject != 'username mention':
                    m.mark_as_read();
                    continue
                
                if check_sub_wait(m.subreddit, sub_wait):
                    continue

                #Add this to our cache
                cache.append(m.id)
                current_sub = m.subreddit

                for reply in m.replies:
                        if reply.author.name == REDDIT_USERNAME:
                            already_done.add(m.id)
                
                #Process the message    
                if m.id not in already_done:
                    #Build reply and send
                    text = parse_comment(m.body)
                    replyto(m, text, already_done)
                    #Mark as read
                    m.mark_as_read();
                    
            
            sleep(SLEEP_TIME)

        except KeyboardInterrupt:
            running = False

        except praw.errors.RateLimitExceeded as pe:
            print(now.strftime("%m-%d-%Y %H:%M"))
            print('ERROR:', pe)
            add_sub_wait(pe.sleep_time, current_sub, sub_wait)
            continue

        except Exception as e:
            now = datetime.datetime.now()
            print(now.strftime("%m-%d-%Y %H:%M"))
            print(traceback.format_exc())
            print('ERROR:', e)
            print('Going to sleep for %i seconds...\n' % (ERROR_SLEEP_TIME))
            sleep(ERROR_SLEEP_TIME)
            continue

#Strip out name and build QR code
def parse_comment(text):
    truncated = False
    match = re.search(SEARCH_TERM, text)
    if match:
        text = text[match.end()+1:]

    text = sanitize_string(text)
    if len(text) > MAX_DATA_LENGTH:
        text = text[:MAX_DATA_LENGTH]
        truncated = True
    data = build_qrcode(text)
    data += get_footer(truncated)
    return data

#Convert unicode to ascii
def sanitize_string(string):
    clean = string.strip().replace(u'\u2019', u'\'')
    return unicodedata.normalize('NFKD', clean).encode('ascii', errors='backslashreplace')

#Footer links
def get_footer(truncated):
    footer = ''
    if len(FOOTER_INFO) > 0:
        footer = '\n%s' % FOOTER_INFO
    if truncated:
        footer += ' *^Note: ^Data ^truncated ^to ^%i ^characters*' % MAX_DATA_LENGTH
    return footer

#QR code parsing
def build_qrcode(data):
    text = ''
    code = pyqrcode.create(data).text()
    lines = code.split('\n')
    for i in range(int(len(lines)/2)):
        text += '    '
        for j in range(len(lines[i*2])):
            text += DATA_BLOCKS[lines[i*2][j]+lines[i*2+1][j]]
        text += '\n'
    return text

#replies to given comment
def replyto(c, text, done):
    now = datetime.datetime.now()
    print((len(done) + 1), 'ID:', c.id, 'Author:', c.author.name, 'r/' + str(c.subreddit.display_name), 'Title:', c.submission.title)
    print (now.strftime("%m-%d-%Y %H:%M"), '\n')


    c.reply(text)
    #print text
    done.add(c.id)

def check_sub_wait(subreddit, subs):
    s = subreddit.display_name
    if s in subs:
        now = time.time()
        wait_time = subs[s]
        print('%i < %i?' % (now, wait_time))
        if now >= wait_time:
            del subs[s]
        else:
            return True
    return False

def add_sub_wait(sleep_time, subreddit, subs):
    now = time.time()
    s = subreddit.display_name
    subs[s] = now+sleep_time

main()