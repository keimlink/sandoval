from django.contrib import admin
from sandoval.movie.models import Director, Cast, Feed, Movie, Person

admin.site.register(Director)
admin.site.register(Cast)
admin.site.register(Feed)
admin.site.register(Movie)
admin.site.register(Person)