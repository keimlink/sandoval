from PIL import Image
import re
import urllib
import warnings

import BeautifulSoup
import imdb

from django.core.management import setup_environ
from django.template import defaultfilters
from sandoval import settings
# Setting up the environment is necessary to import the models.
setup_environ(settings)
from sandoval.movie import models

class InsertionError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class ImageWriter(object):
    KIND_MOVIE = 'movies'
    KIND_PERSON = 'persons'

    @classmethod
    def save(self, url, dest_file, kind=None):
        path = 'images/'
        if kind is not None:
            path = path + kind + '/'
        path = path + dest_file + re.search('.*(\..*)', url).group(1)
        urllib.urlretrieve(url, settings.MEDIA_ROOT + path)
        return (path,) + Image.open(settings.MEDIA_ROOT + path).size

class Movie(object):
    def __init__(self, title):
        # Suppress imdb warnings.
        warnings.filterwarnings('ignore', 
            'unable to use "lxml": No module named lxml')
        warnings.filterwarnings('ignore', 'falling back to "beautifulsoup".')
        try:
            self.find(title)
            (directors, cast, movie_model) = self.create()
            for director in directors:
                self.add_director(director, movie_model)
            for actor in cast:
                self.add_actor(actor, movie_model)
        except InsertionError, exception:
            print exception.message
        finally:
            print 'Done.\n'
    
    def find(self, title):
        print 'Searching for movie "%s".' % title
        ia = imdb.IMDb()
        search_result = ia.search_movie(title, 1)
        if len(search_result) == 0:
            raise InsertionError, 'Movie not found!'
        self.imdb_data = search_result[0]
        self.exists(self.imdb_data.getID())
        ia.update(self.imdb_data)
        print '\tFound "%s".' % self.imdb_data['title']
    
    def exists(self, imdb_id):
        result = models.Movie.objects.filter(imdb_id__exact=imdb_id)
        if len(result) > 0:
            raise InsertionError, 'Movie already exists in database!'
    
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
        if self.imdb_data.has_key('cover url'):
            try:
                image = ImageWriter.save(self.imdb_data['cover url'], 
                    movie.slug, ImageWriter.KIND_MOVIE)
                movie.image = image[0]
                movie.width = image[1]
                movie.height = image[2]
                print '\tSaved image "%s".' % image[0]
            except Exception, exception:
                print '\tError while saving image: %s.' % exception.__str__()
        movie.save()
        print '\tSaved movie.'
        return (self.imdb_data.get('director', []),
                self.imdb_data.get('cast', []),
                movie)
    
    def add_director(self, director, movie_model):
        Person(director, movie_model, True)
    
    def add_actor(self, actor, movie_model):
        Person(actor, movie_model)

class Person(object):
    def __init__(self, person, movie_model, is_director=False):
        ia = imdb.IMDb()
        self.person = person
        ia.update(self.person)
        self.model = self.exists(person.getID())
        if self.model == False:
            self.model = self.create(is_director)
        else:
            print '\tPerson "%s" already exists.' % self.person['name']
            if is_director:
                # The is_director property is initially set when the Person
                # model is created. A person can only become a director and can
                # never lose this status.
                self.model.is_director = is_director
        self.model.save()
        self.build_relation(movie_model, is_director)
        print '\t\tSaved person.'
    
    def exists(self, imdb_id):
        result = models.Person.objects.filter(imdb_id__exact=imdb_id)
        if len(result) > 0:
            return result[0]
        return False
    
    def create(self, is_director):
        model = models.Person()
        print '\tImporting person "%s".' % self.person['name']
        model.canonical_name = self.person['canonical name']
        try:
            # Try to set the slug.
            model.slug = defaultfilters.slugify(self.person['name'])
        except IntergrityError:
            # Setting the slug failed because the value was not unique.
            model.slug = defaultfilters.slugify(self.person['name'] + ' ' + 
                self.person.getID())
        if self.person.has_key('birth date'):
            model.birthdate = self.person['birth date']
        if self.person.has_key('birth notes'):
            model.birthplace = self.person['birth notes']
        if self.person.has_key('mini biography'):
            model.biography = self.person['mini biography'][0].split('::')[0]
        if self.person.has_key('headshot'):
            try:
                image = ImageWriter.save(self.person['headshot'], model.slug, 
                    ImageWriter.KIND_PERSON)
                model.image = image[0]
                model.width = image[1]
                model.height = image[2]
                print '\t\tSaved image "%s".' % image[0]
            except Exception, exception:
                print '\t\tError while saving image: %s.' % exception.__str__()
        model.is_director = is_director
        model.imdb_id = self.person.getID()
        return model
    
    def build_relation(self, movie_model, is_director):
        if is_director:
            self._add_relation_director(movie_model)
        else:
            self._add_relation_actor(movie_model)
    
    def _add_relation_director(self, movie_model):
        if self.person.has_key('director'):
            movies = [movie.getID() for movie in self.person['director']]
            if movie_model.imdb_id in movies:
                models.Director(movie=movie_model, 
                    director=self.model).save()
                print '\t\tAdded as director.'
    
    def _add_relation_actor(self, movie_model):
        key = ''
        if self.person.has_key('actor'):
            key = 'actor'
        elif self.person.has_key('actress'):
            key = 'actress'
        if len(key) > 0:
            movies = [movie.getID() for movie in self.person[key]]
            if movie_model.imdb_id in movies:
                cast = models.Cast()
                cast.role = self.person.currentRole.__str__()
                cast.movie = movie_model
                cast.actor = self.model
                cast.save()
                print '\t\tAdded role "%s".' % cast.role
    
    def save(self):
        return self.model.save()
