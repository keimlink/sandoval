from django.shortcuts import render_to_response
from django.db import connection
from tagging.models import TaggedItem
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from models import Movie, Person

def movie(request, slug):
    movie = Movie.objects.select_related().get(slug=slug)
    menu_active = "movie"
    return render_to_response("movie.html", locals())

def movies(request, order_by="-created", genre=""):
    if genre :
        movies = TaggedItem.objects.get_by_model(Movie.objects.order_by(order_by), [genre])
    else:
        movies = Movie.objects.order_by(order_by)
    
    return render_to_response("movies.html", 
        dict({ 'menu_active' : 'movie' }, **__paginate(movies, request.GET.get('page', '1'), 20)))

def persons(request, order_by="-created"):
    persons = Person.objects.order_by(order_by);
    return render_to_response("persons.html", 
        dict({ 'menu_active' : 'person' }, **__paginate(persons, request.GET.get('page', '1'), 20)))

def person(request, slug):
    menu_active = "person"
    person = Person.objects.get(slug=slug)
    return render_to_response("person.html", locals())

def __paginate(objects, page, paginate_by):
    paginator = Paginator(objects, paginate_by)
    
    try:
        page = int(page)
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        result = paginator.page(page)
    except (EmptyPage, InvalidPage):
        result = paginator.page(paginator.num_pages)
    return {
       'object_list' : result.object_list,
       'page' : result.number,
       'pages' : paginator.num_pages,
       'is_paginated' : paginator.num_pages > 1,
       'has_next' : result.has_next(),
       'has_previous' : result.has_previous(),
       'next' : result.next_page_number(),
       'previous' : result.previous_page_number(),
    }
    
