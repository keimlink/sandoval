import re
import sys
import warnings

import BeautifulSoup
import feedparser
import imdb

from django.core.management import setup_environ
from sandoval import settings
# Setting up the environment is necessary to import the models.
setup_environ(settings)
from sandoval.movie import models

class Movie(object):
    def __init__(self, title):
        # Suppress imdb warnings.
        warnings.filterwarnings('ignore', 'unable to use "lxml": No module named lxml')
        warnings.filterwarnings('ignore', 'falling back to "beautifulsoup".')
        try:
            self.find(title)
            (directors, cast) = self.create()
            for director in directors:
                self.add_director(director)
            for person in cast:
                self.add_cast(person)
        except Exception, e:
            print '\t%s' % e.message
        finally:
            print '--------------------------------------------------------------------------------'
    
    def find(self, title):
        print 'Searching for movie "%s".' % title
        ia = imdb.IMDb()
        search_result = ia.search_movie(title, 1)
        if len(search_result) == 0:
            raise Exception, 'Movie not found!'
        self.imdb_data = search_result[0]
        self.exists(self.imdb_data.getID())
        ia.update(self.imdb_data)
        print '\tFound "%s".' % self.imdb_data['title']
    
    def exists(self, imdb_id):
        result = models.Movie.objects.filter(imdb_id__exact=imdb_id)
        if len(result) > 0:
            raise Exception, 'Movie already exists in database!'
    
    def create(self):
        movie = models.Movie()
        movie.title = self.imdb_data['title']
        plot = self.imdb_data.get('plot', ['::'])[0].split('::')
        movie.plot = plot[0]
        movie.plot_author = plot[1]
        movie.year = self.imdb_data['year']
        movie.runtime = int(re.search(
            '\d+', self.imdb_data.get('runtimes', ['0'])[0]).group(0))
        movie.rating = self.imdb_data.get('rating', 0.0)
        movie.genres = ', '.join(self.imdb_data.get('genres', []))
        movie.imdb_id = self.imdb_data.movieID
        movie.save()
        print '\tSaved movie.'
        return (self.imdb_data.get('art direction', []),
                self.imdb_data.get('cast', []))
    
    def add_director(self, name):
        pass
    
    def add_cast(self, name):
        pass

class Person(object):
    def __init__(self, person):
        self.imdb_data = person
        self.model = models.Person()
        self.create()
        pass
    
    def exists(self):
        pass
    
    def is_director(self):
        pass
    
    def is_cast(self):
        pass
    
    def create(self):
        print 'Importing person "%s"' % self.imdb_data
        pass
    
    def make_director(self, movie):
        pass

class Rss(object):
    def __init__(self, url):
        try:
            print '\nTesting %s' % url
            feedparser.urllib.urlopen(url)
        except IOError, e:
            raise Exception, e.__str__()
        else:
            print 'Fetching %s' % url
            print '--------------------------------------------------------------------------------'
            self.feed = feedparser.parse(url)
    
    def __iter__(self):
        for entry in self.feed.entries:
            yield entry.title

class Dispatcher(object):
    def __init__(self):
        for feed in models.Feed.objects.all():
            try:
                for entry in Rss(feed.url):
                    Movie(entry)
            except Exception, e:
                print e.message

if __name__ == '__main__':
    Dispatcher()
