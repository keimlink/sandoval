import re
import warnings

import BeautifulSoup
import imdb

from django.core.management import setup_environ
from django.template import defaultfilters
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
            (directors, cast, movie_model) = self.create()
            for director in directors:
                self.add_director(director, movie_model)
            for person in cast:
                self.add_cast(person, movie_model)
        except Exception, e:
            print '\t%s' % e.message
        finally:
            print 'Done.\n'
    
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
        movie.slug = defaultfilters.slugify(self.imdb_data['title'] + ' ' 
            + self.imdb_data['year'].__str__())
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
        return (self.imdb_data.get('director', []),
                self.imdb_data.get('cast', [])[:9],
                movie)
    
    def add_director(self, person, movie_model):
        Person(person, movie_model, True)
    
    def add_cast(self, person, movie_model):
        Person(person, movie_model)

class Person(object):
    def __init__(self, person, movie_model, is_director=False):
        self.model = self.exists(person.getID())
        if self.model == False:
            self.model = self.create(person.getID())
        self.model.is_director = is_director
        self.build_relation(movie_model)
        self.model.save()
        print '\tSaved person "%s".' % person['name']
    
    def exists(self, imdb_id):
        result = models.Person.objects.filter(imdb_id__exact=imdb_id)
        if len(result) > 0:
            return result[0]
        return False
    
    def create(self, imdb_id):
        ia = imdb.IMDb()
        person = ia.get_person(imdb_id)
        model = models.Person()
        print '\tImporting person "%s".' % person['name']
        name = person['canonical name'].split(', ')
        if len(name) == 2:
            model.forename = name[1]
        model.surname = name[0]
        try:
            # Try to set the slug.
            model.slug = defaultfilters.slugify(person['name'])
        except IntergrityError:
            # Setting the slug failed because the value was not unique.
            model.slug = defaultfilters.slugify(person['name'] + ' ' + 
                person.getID())
        if person.has_key('birth date'):
            model.birthdate = person['birth date']
        if person.has_key('birth notes'):
            model.birthplace = person['birth notes']
        if person.has_key('mini biography'):
            model.biography = person['mini biography'][0].split('::')[0]
        model.imdb_id = person.getID()
        return model
    
    def build_relation(self, movie_model):
        pass
    
    def save(self):
        return self.model.save()
