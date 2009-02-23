from django.shortcuts import render_to_response
from models import Movie, Person
from django.db import connection


def get_detailed_movies(request, order_by, limit=10):
    return render_to_response("detailed_movies.html", {"movies" : Movie.objects.order_by(order_by)[:limit], })

def get_movie(request, slug):
    movie = Movie.objects.select_related().get(slug=slug)
    return render_to_response("movie.html", locals())

def get_movies(request, limit=10, order_by="-created"):
    return render_to_response("movies.html", {"movies" : Movie.objects.order_by(order_by)[:limit]})

def get_persons(request, limit=10, order_by="-created"):
    return render_to_response("persons.html", {"persons" : Person.objects.order_by(order_by)[:limit]})

def get_person(request, slug):
    return render_to_response("person.html", {"person" : Person.objects.get(slug=slug)})