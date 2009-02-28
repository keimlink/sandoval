# -*- coding: utf-8 -*-

from django.db import models
from tagging.fields import TagField
from tagging.fields import Tag

class Abstract(models.Model):
    STATUS_INVISIBLE = 0
    STATUS_VISIBLE = 1
    STATUS_CHOICES = (
        (STATUS_VISIBLE, 'anzeigen'),
        (STATUS_INVISIBLE, 'nicht anzeigen')
    )
    visible = models.SmallIntegerField('Status', choices=STATUS_CHOICES,
        help_text='Definiert ob dieser Datensatz sichtbar ist oder nicht.',
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
    slug = models.SlugField(unique=True, help_text='Der Inhalt dieses Feldes \
        wird automatisch aus Vornamen und Nachnamen erzeugt und darf nur \
        einmal vorkommen.')
    birthdate = models.CharField('Geburtsdatum', max_length=100, blank=True)
    birthplace = models.CharField('Geburtsort', max_length=200, blank=True)
    biography = models.TextField('Biografie', blank=True)
    is_director = models.BooleanField('Regisseur', 
        help_text='Wenn diese Checkbox aktiviert ist kann die Person als \
        Regisseur ausgewählt werden.')
    imdb_id = models.CharField('IMDB ID', max_length=10)
    image = models.ImageField('Foto', upload_to='images/actors', blank=True,
        height_field='height', width_field='width')
    height = models.IntegerField('Höhe', editable=False, null=True)
    width = models.IntegerField('Breite', editable=False, null=True)
    
    class Meta():
        verbose_name = 'Person'
        verbose_name_plural = 'Personen'
        ordering = ('surname', 'forename')
    
    def __unicode__(self):
        return '%s %s' % (self.forename, self.surname)
    
    def _get_canonical_name(self):
        return '%s, %s' % (self.surname, self.forename)
    
    def _set_canonical_name(self, canonical_name):
        parts = canonical_name.split(', ')
        if len(parts) < 2:
            parts.append('')
        self.surname, self.forename = parts
    
    canonical_name = property(_get_canonical_name, _set_canonical_name)
    
    def cast_count(self):
        return Cast.objects.filter(actor__exact=self).count()
    cast_count.short_description = 'Rollen'
    
    def director_count(self):
        return Director.objects.filter(director__exact=self).count()
    director_count.short_description = 'Regie'
    
    def thumbnail(self):
        if len(self.image.name) == 0:
            return '<img src="/static/images/persons/dummy.png" width="45" \
                heigth="70" alt="Kein Foto" />'
        return '<img src="%s" width="%d" heigth="%d" alt="%s"/>' % \
            (self.image.url, self.width / 2, self.height / 2, self.image.name)
    thumbnail.allow_tags = True
    thumbnail.short_description = 'Foto'
    thumbnail.admin_order_field = 'image'
    
    def get_absulote_url(self):
        return '/person/' + self.slug

class Movie(Abstract):
    title = models.CharField('Titel', max_length=200)
    slug = models.SlugField(unique=True, help_text='Der Inhalt dieses Feldes \
        wird automatisch aus dem Titel und dem Jahr erzeugt und darf nur \
        einmal vorkommen.')
    plot = models.TextField('Handlung', blank=True)
    plot_author = models.CharField('Autor', max_length=100, blank=True,
        help_text='Autor der Handlung.')
    year = models.IntegerField('Jahr', max_length=4)
    runtime = models.IntegerField('Laufzeit', blank=True,
        help_text='Laufzeit in Minuten angeben.')
    rating = models.FloatField('Bewertung', blank=True,
        help_text='Bewertung als Fliesskommazahl auf einer Skala von 0 bis 10.')
    genres = TagField('Genres', help_text='Kommagetrennte Liste der Genres.')
    imdb_id = models.CharField('IMDB ID', max_length=10)
    image = models.ImageField('Poster', upload_to='images/movies', blank=True,
        height_field='height', width_field='width')
    height = models.IntegerField('Höhe', editable=False, null=True)
    width = models.IntegerField('Breite', editable=False, null=True)
    directors = models.ManyToManyField(Person, through='Director')
    actors = models.ManyToManyField(Person, through='Cast', 
        related_name='actor_set')
    
    class Meta():
        verbose_name = 'Film'
        verbose_name_plural = 'Filme'
        ordering = ('title',)
    
    def __unicode__(self):
        return '%s (%d)' % (self.title, self.year)
    
    @property
    def genres_list(self):
        return Tag.objects.get_for_object(self)
    
    def director(self):
        return ', '.join([person.__str__() for person in self.directors.all()])
    director.short_description = 'Regisseur(e)'
    
    def thumbnail(self):
        if len(self.image.name) == 0:
            return '<img src="/static/images/movies/dummy.png" width="45" \
                heigth="70" alt="Kein Poster" />'
        return '<img src="%s" width="%d" heigth="%d" alt="%s"/>' % \
            (self.image.url, self.width / 2, self.height / 2, self.image.name)
    thumbnail.allow_tags = True
    thumbnail.short_description = 'Poster'
    thumbnail.admin_order_field = 'image'
    
    def get_absolute_url(self):
        return '/movies/' + self.slug

class Director(models.Model):
    movie = models.ForeignKey(Movie, verbose_name='Film')
    director = models.ForeignKey(Person, verbose_name='Regisseur', 
        limit_choices_to={'is_director__exact': True})
    
    class Meta():
        verbose_name = 'Regisseur'
        verbose_name_plural = 'Regisseure'
        ordering = ('director__surname', 'movie')
    
    def __unicode__(self):
        return self.director.__str__()

class Cast(models.Model):
    role = models.CharField('Rolle', max_length=100)
    movie = models.ForeignKey(Movie, verbose_name='Film')
    actor = models.ForeignKey(Person, verbose_name='Person')
    
    class Meta():
        verbose_name = 'Rolle'
        verbose_name_plural = 'Rollen'
        ordering = ('movie',)
    
    def __unicode__(self):
        return self.role.__str__()

class Feed(models.Model):
    FIELD_TITLE = 'title'
    FIELD_DESCRIPTION = 'description'
    FIELD_CHOICES = (
        (FIELD_TITLE, FIELD_TITLE),
        (FIELD_DESCRIPTION, FIELD_DESCRIPTION)
    )
    title = models.CharField('Name', max_length=100)
    url = models.URLField('URL')
    field = models.CharField('Feld', max_length=30, choices=FIELD_CHOICES,
        default=FIELD_TITLE, help_text='Feld des Feeds, das ausgelesen werden \
        soll.')
    regexp = models.CharField('Regulärer Ausdruck', max_length=100, 
        default='(.*)', help_text='Regulärer ausdruck, der auf das \
        ausgewählte Feld angewendet wird.')
    
    class Meta():
        verbose_name = 'Feed'
        verbose_name_plural = 'Feeds'
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title
