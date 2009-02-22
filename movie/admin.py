from django.contrib import admin
from sandoval.movie.models import Director, Cast, Feed, Movie, Person

class EntryMovie(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', 'year')}

class EntryPerson(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('forename', 'surname')}

admin.site.register(Director)
admin.site.register(Cast)
admin.site.register(Feed)
admin.site.register(Movie, EntryMovie)
admin.site.register(Person, EntryPerson)