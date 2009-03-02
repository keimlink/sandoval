from django.shortcuts import render_to_response
from django.db.models import Q
from django.db import connection
from tagging.models import TaggedItem
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from models import Movie, Person

def movie(request, slug):
    movie = Movie.objects.select_related().get(slug=slug)
    menu_active = "movie"
    return render_to_response("movie.html", locals())

def movies(request, order_by="-created", genre=""):
    name = request.GET.get('name', '')
    if name:
        movies = Movie.objects.filter(title__icontains=name)
    else:
        movies = Movie.objects.all()
    if genre:
        movies = TaggedItem.objects.get_by_model(movies, [genre])
    return render_to_response("movies.html", 
        dict({ 'menu_active' : 'movie', 'name' : name }, **__paginate(movies, request.GET.get('page', '1'), 20)))

def persons(request, order_by="-created"):
    name = request.GET.get('name', '')
    if name:
        persons = Person.objects.filter(Q(surname__icontains=name) | Q(forename__icontains=name))
    else:
        persons = Person.objects.all()
#    persons = Person.objects.order_by(order_by);
    return render_to_response("persons.html", 
        dict({ 'menu_active' : 'person', 'name' : name }, **__paginate(persons, request.GET.get('page', '1'), 20)))

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