# -*- coding: utf-8 -*-

from django.db import models

class Abstract(models.Model):
    STATUS_INVISIBLE = 0
    STATUS_VISIBLE = 1
    STATUS_CHOICES = (
        (STATUS_VISIBLE, 'anzeigen'),
        (STATUS_INVISIBLE, 'nicht anzeigen')
    )
    visible = models.SmallIntegerField('Status', choices=STATUS_CHOICES,
        default=STATUS_VISIBLE)
    created = models.DateTimeField('erstellt am', editable=False,
        auto_now_add=True)
    edited = models.DateTimeField('zuletzt bearbeitet am', editable=False,
        auto_now=True)
    
    class Meta:
        abstract = True

class Person(Abstract):
    forename = models.CharField('Vorname', max_length=100)
    surname = models.CharField('Nachname', max_length=100)
    birthdate = models.DateField('Geburtsdatum')
    birthplace = models.CharField('Geburtsort', max_length=200, blank=True)
    is_director = models.BooleanField('Regisseur', 
        help_text='Wenn diese Checkbox aktiviert ist kann die Person als Regisseur ausgewählt werden.')
    image = models.ImageField('Foto', upload_to='images/actors', blank=True,
        height_field='height', width_field='width')
    width = models.IntegerField('Breite', editable=False, null=True)
    height = models.IntegerField('Höhe', editable=False, null=True)
    biography = models.TextField('Biografie', blank=True)
    
    class Meta():
        verbose_name = 'Person'
        verbose_name_plural = 'Personen'
        ordering = ['surname', 'forename']
    
    def __unicode__(self):
        return '%s %s' % (self.forename, self.surname)
    
    def get_absulote_url(self):
        return '/person/' + self.id

class Movie(Abstract):
    title = models.CharField('Titel', max_length=200)
    year = models.IntegerField('Jahr', max_length=4)
    description = models.TextField('Inhalt', blank=True)
    image = models.ImageField('Poster', upload_to='images/movies', blank=True,
        height_field='height', width_field='width')
    width = models.IntegerField('Breite', editable=False, null=True)
    height = models.IntegerField('Höhe', editable=False, null=True)
    directors = models.ManyToManyField(Person, through='Director')
    actors = models.ManyToManyField(Person, through='Cast', related_name='actor_set')
    runtime = models.IntegerField('Laufzeit', blank=True)
    rating = models.FloatField('Bewertung', blank=True)
    #tags
    
    class Meta():
        verbose_name = 'Film'
        verbose_name_plural = 'Filme'
        ordering = ['title', 'year']
    
    def __unicode__(self):
        return '%s (%d)' % (self.title, self.year)
    
    def get_absolute_url(self):
        return '/movies/' + self.id

class Director(models.Model):
    movie = models.ForeignKey(Movie)
    director = models.ForeignKey(Person,
        limit_choices_to={'is_director__exact': True})
    
    class Meta():
        verbose_name = 'Regisseur'
        verbose_name_plural = 'Regisseure'
    
    def __unicode__(self):
        return self.director.__str__()

class Cast(models.Model):
    role = models.CharField('Rolle', max_length=100)
    movie = models.ForeignKey(Movie)
    actor = models.ForeignKey(Person)
    
    class Meta():
        verbose_name = 'Schauspieler'
        verbose_name_plural = 'Schauspieler'
    
    def __unicode__(self):
        return self.role.__str__()
