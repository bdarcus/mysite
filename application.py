#!/usr/bin/env python
import sys
from sys import exit, exc_info
from os.path import dirname, join, split, splitext, expanduser
import web
from web.utils import safemarkdown
from bibo.models import *
from rdfalchemy.engine import *
from rdflib import ConjunctiveGraph, Namespace, Literal, URIRef
import markdown2
import urlparse

"""
copyright Bruce D'Arcus (2008)
"""
# load config file
try:
    config_file = os.path.join(os.path.dirname(__file__), 'config.py')
    config = eval(open(config_file).read())
except IOError, (errno, strerror):
    print "I/O error(%s): %s" % (errno, strerror)
except ValueError:
    print "Could not convert data to an integer."
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise

graph = rdfSubject.db = engine_from_config(config)

urls = (
  '/', 'Home',
  '/colophon', 'Colophon',
  '/notes', 'Notes',
  '(/categories/)(.*)', 'Category',
  '(/notes/)(.*)', 'DocItem',
  '(/publications/)(.*)', 'DocItem',
  '/about',  'About',
  '/categories', 'Categories',
  '/photos', 'Photos',
  '/publications', 'Publications',
  )

def get_relative_uri(uri):
    return urlparse.urlsplit(uri)[2]

render = web.template.render('templates/', cache=False)
web.template.Template.globals['render'] = render 
web.template.Template.globals['rel_uri'] = get_relative_uri 
web.template.Template.globals['markdown'] = markdown2.markdown

app = web.application(urls, globals())

about = Person(URIRef(config['about.uri']))
notes = []
photos = []
articles = []
books = []
categories = []

for article in AcademicArticle.ClassInstances():
    articles.append(article)

for book in Book.ClassInstances():
    books.append(book)

for photo in Image.ClassInstances():
    photos.append(photo)

for note in Note.ClassInstances():
    notes.append(note)

for category in Concept.ClassInstances():
    categories.append(category)

class Home:
     def GET(self):
         return(render.home(about))

class About:
     def GET(self):
         return(render.about(about))

class Colophon:
     def GET(self):
         return(render.colophon())

class Categories:
     def GET(self):
         return(render.categories("Categories", categories))

class Notes:
     def GET(self):
         return(render.index("Notes", notes))

def get_content(basedir, uri):
    print uri
    filename = urlparse.urlsplit(uri)[-3]
    print filename
    filepath = config['site.content_dir'] + filename
    print filepath
    try:
        return open(filepath).read()
    except:
        "file not found"

class Category:
    def GET(self, basedir, slug):
        uri = config['rdfalchemy.identifier'] + basedir + slug
        category = Concept(URIRef(uri))
        link_uri = basedir + slug
        return(render.category(category, link_uri))

class DocItem:
    
    def GET(self, basedir, slug):
         uri = config['rdfalchemy.identifier'] + basedir + slug
         doc = Document(URIRef(uri))
         content_uri = doc.formats[0] if doc.formats else None
         content = get_content(basedir, content_uri.resUri) if content_uri else None
         return(render.item(doc, content))

class Photos:
     def GET(self):
         return(render.index("Photos", photos))

class Publications:
     def GET(self):
         return(render.publications("Publications", articles, books))

if __name__ == "__main__": app.run()


