from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from movie.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^sandoval/', include('sandoval.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    # Movies.
    (r'^movie/(?P<slug>.+)$', get_movie),
    (r'^movies/detailed$', get_detailed_movies, {'order_by': 'title'}),
    (r'^$', get_detailed_movies, {'limit': 10, 'order_by':'-created'}),
    (r'^movies/detailed/orderby/(?P<order_by>.*?)/limit/(?P<limit>.*?)/$', 
        get_detailed_movies),
    (r'^movies/detailed/orderby/(?P<order_by>.*?)/$', get_detailed_movies),
    (r'^movies$', get_movies, {'order_by': 'title'}),
    (r'^movies/orderby/(?P<order_by>.*)/$', get_movies),
    # Persons.
    (r'^persons/orderby/(?P<order_by>.*)/$', get_persons),
    (r'^person/(?P<slug>.+)$', get_person),
    # URL of the media directory / static content. In a productive environment
    # this would be served by an extra server and not by Django.
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
