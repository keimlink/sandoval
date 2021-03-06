from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import list_detail
from movie.models import Movie

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
    (r'^pages', include('django.contrib.flatpages.urls')),
    (r'^comments/', include('django.contrib.comments.urls')), 
    # Movies.
    (r'^$', list_detail.object_list, 
        {
            'queryset' : Movie.objects.order_by(), 
            'paginate_by' : 5, 'allow_empty' : True, 
            'template_name' : 'detailed_movies.html',
            'extra_context' : { 
                'menu_active' : 'home', 
             }
        },
        'detailed-movies'),
    (r'^movies/$', movies),
    (r'^movies/genre/(?P<genre>.*?)/$', movies),
    (r'^movies/(?P<slug>.+)$', movie),
    # Persons.
    (r'^persons/$', persons),
    (r'^persons/(?P<slug>.+)$', person),
    (r'^persons/(?P<slug>.+)$', person),
    
    # URL of the media directory / static content. In a productive environment
    # this would be served by an extra server and not by Django.
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
