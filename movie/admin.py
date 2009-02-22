from django.contrib import admin
from sandoval.movie.models import Director, Cast, Feed, Movie, Person

class EntryCast(admin.ModelAdmin):
    list_display = ('role', 'actor', 'movie')

class EntryDirector(admin.ModelAdmin):
    list_display = ('director', 'movie')

class EntryFeed(admin.ModelAdmin):
    list_display = ('title', 'url')

class EntryMovie(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title', 'year', 'slug', 'imdb_id', 'visible']}),
        ('Inhalt', {'fields': ['plot', 'plot_author']}),
        ('Weitere Informationen', {'fields': ['runtime', 'rating', 'genres', 
            'image']})
    ]
    prepopulated_fields = {'slug': ('title', 'year')}
    list_display = ('title', 'year', 'get_director', 'rating', 'genres', 
        'edited')
    list_filter = ['edited', 'year']
    search_fields = ['title']

class EntryPerson(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['forename', 'surname', 'slug', 'imdb_id', 'visible']}),
        ('Weitere Informationen', {'fields': ['is_director', 'birthdate', 
            'birthplace', 'biography', 'image']})
    ]
    prepopulated_fields = {'slug': ('forename', 'surname')}
    list_display = ('surname', 'forename', 'is_director', 'get_cast_count', 
        'get_director_count', 'edited')
    list_filter = ['edited', 'is_director']
    search_fields = ['surname', 'forename']

admin.site.register(Director, EntryDirector)
admin.site.register(Cast, EntryCast)
admin.site.register(Feed, EntryFeed)
admin.site.register(Movie, EntryMovie)
admin.site.register(Person, EntryPerson)