import re

import feedparser

from django.core.management import setup_environ
from models import Movie
from sandoval import settings
# Setting up the environment is necessary to import the models.
setup_environ(settings)
from sandoval.movie.models import Feed

class Rss(object):
    def __init__(self, feed_model):
        self.field = feed_model.field
        self.regexp = feed_model.regexp
        try:
            print '\nParsing "%s".' % feed_model.title
            print 'Testing %s' % feed_model.url
            feedparser.urllib.urlopen(feed_model.url)
        except IOError, exception:
            raise Exception, exception.__str__()
        else:
            print 'Fetching %s\n' % feed_model.url
            self.feed = feedparser.parse(feed_model.url)
    
    def __iter__(self):
        for entry in self.feed.entries:
            yield re.search(self.regexp, entry.get('title')).group(1)

class Dispatcher(object):
    def __init__(self):
        feeds = Feed.objects.all()
        if len(feeds) > 0:
            for feed in feeds:
                try:
                    for entry in Rss(feed):
                        Movie(entry)
                except Exception, exception:
                    print exception.message
        else:
            print 'No feeds found in database!'

if __name__ == '__main__':
    Dispatcher()
