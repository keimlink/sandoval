from django.contrib import admin
from sandoval.movie.models import Movie, Person, Director, Cast

admin.site.register(Movie)
admin.site.register(Person)
admin.site.register(Director)
admin.site.register(Cast)