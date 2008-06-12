#!/usr/bin/env python
import sys
from sys import exit, exc_info
from os.path import dirname, join, split, splitext, expanduser
import web
from web.utils import safemarkdown
from bibo.models import *
from rdfalchemy.engine import *
from rdflib import ConjunctiveGraph, Namespace, Literal, URIRef
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib import plugin

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

store = plugin.get('MySQL', Store)('rdflib_db')
store.open(config['rdflib.config'])

graph = rdfSubject.db = ConjunctiveGraph(store)

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
  '/links', 'Links',
  '/publications', 'Publications',
  )

def get_relative_uri(uri):
    return urlparse.urlsplit(uri)[2]

render = web.template.render('templates/', cache=False)
web.template.Template.globals['render'] = render 
web.template.Template.globals['rel_uri'] = get_relative_uri 
web.template.Template.globals['markdown'] = markdown2.markdown

app = web.application(urls, globals())

me = Person(URIRef(config['about.uri']))
notes = []
photos = []
articles = []
books = []
categories = []
bookmarks = []

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

for bookmark in Bookmark.ClassInstances():
    bookmarks.append(bookmark)

bookmarks.sort()
books.sort()
articles.sort()
categories.sort()

class Home:
     def GET(self):
         return(render.home(me))

class About:
     def GET(self):
         return(render.about(me))

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
    """
    Find locals content files that conform to same dir 
    structure as URI. Local basedir is configured in 
    config.py.
    """
    filename = urlparse.urlsplit(uri)[-3]
    filepath = config['site.content_dir'] + filename
    try:
        return open(filepath).read()
    except:
        "file not found"

class Category:
    def GET(self, basedir, slug):
        uri = config['rdfalchemy.identifier'] + basedir + slug
        category = Concept(URIRef(uri))
        # need to grab related rdfSubject instances using the subjects attribute
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

class Links:
    def GET(self):
        return(render.links(bookmarks))

class Publications:
    def GET(self):
        return(render.publications("Publications", articles, books))

print len(bookmarks), " Bookmark instances."
print len(categories), " Concept instances."

if __name__ == "__main__": app.run()


