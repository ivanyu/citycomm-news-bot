#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A Twitter news bot for http://citycomm.ru/news
Works with both Python 2 and 3.

The configuration must be put in "config.json" (see "dummy_config.json").


MIT License
Copyright (C) 2013 Ivan Yurchenko

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import with_statement
from __future__ import unicode_literals

import sys
import logging
import logging.handlers
import json
from urlparse import urljoin
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import lxml.html
import tweepy


CONFIG_FILE = 'config.json'
LAST_POSTED_FILE = 'last_posted.txt'


def read_config():
    ERROR_MESSAGE = "Configuration error"
    try:
        with open(CONFIG_FILE, 'r') as fp:
            config = json.load(fp)
            try:
                assert 'twitter' in config
                assert 'consumer_key' in config['twitter']
                assert 'consumer_secret' in config['twitter']
                assert 'access_token' in config['twitter']
                assert 'access_token_secret' in config['twitter']
            except AssertionError:
                logging.critical(ERROR_MESSAGE)
                exit(1)
            return config
    except IOError:
        logging.critical(ERROR_MESSAGE)
        exit(1)


def get_last_posted_id():
    try:
        with open(LAST_POSTED_FILE, 'r') as fp:
            last_id = fp.readline()
            return last_id
    except IOError:
        return None


def save_last_posted_id(id):
    with open(LAST_POSTED_FILE, 'w') as fp:
        fp.write(id)


def get_news(base_url):
    page = urlopen(urljoin(base_url, 'news')).read()
    doc = lxml.html.document_fromstring(page)
    news = [(a.attrib['href'].split('/')[-1].split('.')[0],
             urljoin(base_url, a.attrib['href']),
             a.text.strip())
            for a in doc.xpath('.//dl[@class="news"]/dt/a')]
    return news


def post(news_item, config):
    auth = tweepy.OAuthHandler(
        config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(
        config['access_token'], config['access_token_secret'])
    api = tweepy.API(auth)
    tweet = '{0} {1}'.format(news_item[2], news_item[1])
    api.update_status(tweet)


def main():
    LOG_LEVEL = logging.CRITICAL

    logging.getLogger().setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler = logging.handlers.RotatingFileHandler(
        'citycomm_bot.log', maxBytes=1024**3)
    # handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    logging.debug('Bot started')

    BASE_URL = 'http://www.citycomm.ru'

    config = read_config()

    last_posted_id = get_last_posted_id()
    last = get_news(BASE_URL)[0]
    if not last_posted_id or last[0] != last_posted_id:
        logging.debug('There is news, ID:{0}'.format(last[0]))
        post(last, config['twitter'])
        logging.debug('News ID={0} successfully posted'.format(last[0]))
        last_posted_id = last[0]
        save_last_posted_id(last_posted_id)
    else:
        logging.debug('No news')

    logging.debug('Bot stopped')


if __name__ == '__main__':
    main()
