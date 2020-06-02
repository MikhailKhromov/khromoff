import logging
import urllib.robotparser

import pymorphy2
import requests

analyzer = pymorphy2.MorphAnalyzer()
logger = logging.getLogger('khromoff.search.scrapper')


def convert_text(text):

    """
    Converts random text into useful text, or returns '' (not usable for search).

    :param text: some random text
    :return: STR - good text
    """
    text = text.lstrip().rstrip()
    if len(text) >= 3:
        percent_numbers_and_symbols = 0
        # only normal sentences or big numbers can be used
        for i in text:
            if i in '0123456789,./-_()!@#$%^&*\'"\\':
                percent_numbers_and_symbols += 1
        try:
            percent_numbers_and_symbols = len(text) / percent_numbers_and_symbols * 100
        except ZeroDivisionError:
            percent_numbers_and_symbols = 0

        if not percent_numbers_and_symbols > 60 or len(text) >= 7:
            words = text.split()
            if len(words) <= 3:
                for i in range(len(words)):
                    words[i] = get_normal_form(words[i])
                words = ' '.join(words)

            # TODO: fix possible misspellings
            return words

    return ''


def get_normal_form(word):
    # яндекса -> яндекс
    return analyzer.parse(word)[0].normal_form


class RobotsTXTParser(urllib.robotparser.RobotFileParser):
    def __init__(self, url=''):
        super().__init__(url=url)

    def can_fetch(self, url):
        return super().can_fetch('*', url)


def get(url):
    headers = {'user-agent': 'khrmff-search-engine 0.0.2a'}
    try:
        resp = requests.get(url, headers=headers).text
    except requests.exceptions.ConnectionError as e:
        logger.warning('Connection error occured - %s' % e)
        return ''
    return resp

