import logging
import time
from abc import ABC
from html.parser import HTMLParser
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from search.models import Page, MetaData
from search.scraping.utils import convert_text, RobotsTXTParser, get

logger = logging.getLogger('khromoff.search.scrapping')


class KhrmffHTMLParser(HTMLParser, ABC):
    data = {'content': '', 'links': [], 'title': '',
            'lang': '', 'description': '', 'text': []}
    current_tag = None
    start_tag = None
    counter = 0
    start = False  # are we in tag which might contain text or not?
    text = []
    a_counter, shit_counter, text_counter = 0, 0, 0

    def feed(self, data):
        self.data['content'] = data
        self.data['links'] = []
        return super().feed(data)

    def get_data(self):
        res = self.data.copy()
        self.data['text'] = self.text
        return res

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.current_tag = tag
        if tag == 'a':
            self.a_counter += 1
            if attrs.get('href'):
                self.data['links'].append({'href': attrs['href']})
                # TODO: add 'use': 'пройдя по этой ссылке можно купить некочан'
        elif tag == 'html':
            if attrs.get('lang'):
                self.data['lang'] = attrs['lang']
        elif tag == 'script' or tag == 'noscript' or tag == 'style':
            self.shit_counter += 1
            self.start = False

    def handle_endtag(self, tag):
        if tag == 'script' or tag == 'noscript' or tag == 'style':
            self.start = True

    def handle_data(self, data):
        if data.lstrip().rstrip() == '':
            return
        if self.start:
            self.text_counter += 1
            text = convert_text(data)

            if text != '':
                self.text.append(text)

        if self.current_tag == 'title':
            self.data['title'] = data


def parse(data):
    parser = KhrmffHTMLParser()
    parser.feed(data)
    return parser.get_data()


def fix_url(org_url, hostname):
    # url = url.split('#')[0].split('?')[0]
    url = org_url['href']
    if url == '':
        raise ValidationError('Invalid URL. - %s' % url)

    parsed = urlparse(url)
    if parsed.netloc == '':
        if url[0] == '/':
            url = hostname[:-1] + url
        else:
            url = hostname + url
    elif parsed.scheme == '':
        if url[:2] == '//':
            url = 'http:' + url

    if url[-1:] != '/':
        url += '/'
    URLValidator()(url)
    return url


def crawl(start_url):
    urls = [start_url]
    pages_visited = [i.url for i in Page.objects.all()]
    domains = {}  # {'yandex.ru': {'robots': {'allowed': ['*'], 'disallowed': []}}}

    while True:
        if len(urls) <= 0:
            logging.error('There are no URL\'s left. Terminating.')
            break

        curr = urls[0]
        logger.info('Parsing page %s' % curr)

        hostname = curr[:1 + curr.find('/', curr.index('://') + 3)]  # https://google.com/test -> https://google.com/

        rb = domains.get(hostname)
        if rb is None:
            rb = RobotsTXTParser()
            rb.set_url(hostname + 'robots.txt')
            rb.read()

            domains[hostname] = rb

        # TODO: use a func here, with headers, and everywhere replace .get() with it.
        if rb.can_fetch(curr):
            resp = get(curr)
        else:
            logger.info('Robot.txt didn\'t allow us to fetch %s' % curr)
            resp = ''

        start = time.perf_counter()
        data = parse(resp)
        stop = time.perf_counter()
        logger.info('Parsed in %f seconds' % (float(stop) - float(start)))

        if 'ru' not in data['lang'].lower():
            # russian language only
            logger.debug('Didn\'t parse because not RU language.')
            pages_visited.append(curr)
            urls.pop(0)
            continue

        lang = 'ru'
        meta = MetaData(lang=lang, description=data['description'],
                        title=data['title'], text=data['text'])
        meta.save()
        Page.objects.create(url=curr, meta=meta)

        for url in data['links']:
            try:
                url = fix_url(url, hostname)
            except ValidationError:
                continue
            if url not in urls and url not in pages_visited:
                urls.append(url)
                # logger.debug('Added url %s' % url)

        pages_visited.append(curr)
        urls.pop(0)
