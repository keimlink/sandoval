from django.shortcuts import render_to_response
from models import Movie, Person
from django.db import connection

def get_detailed_movies(request, order_by, limit=10):
    menu_active = "home"
    movies = Movie.objects.order_by(order_by)[:limit]
    return render_to_response("detailed_movies.html", locals())

def get_movie(request, slug):
    movie = Movie.objects.select_related().get(slug=slug)
    menu_active = "movie"
    return render_to_response("movie.html", locals())

def get_movies(request, limit=10, order_by="-created"):
    menu_active = "movie"
    movies = Movie.objects.order_by(order_by)[:limit]
    return render_to_response("movies.html", locals())

def get_persons(request, limit=10, order_by="-created"):
    menu_active = "person"
    persons = Person.objects.order_by(order_by)[:limit]
    return render_to_response("persons.html", locals())

def get_person(request, slug):
    menu_active = "person"
    person = Person.objects.get(slug=slug)
    return render_to_response("person.html", locals())