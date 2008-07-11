#!/usr/bin/env python
import web
import atexit
from controllers import *
from utils.site import *
from bibo.models import *
from rdflib import ConjunctiveGraph
from rdflib.Graph import Graph
from rdflib.store import Store
from rdflib import plugin
import os
from os.path import dirname, join, split, splitext, expanduser
import markdown2

config_file = os.path.join(os.path.dirname(__file__), 'config.py')
config = eval(open(config_file).read())

store = plugin.get('MySQL', Store)('rdflib_db')
store.open(config['rdflib.config'])

graph = rdfSubject.db = ConjunctiveGraph(store)

urls = (  
   "/", Home,
   "/about", About,
   "/publications", Publications,
   "/categories", Categories,
   "/links", Links,
   "/photos", Photos,
   "/publications/articles/(.*)", ArticlePublication,
   "/publications/books/(.*)", BookPublication,
   "/publications/chapters/(.*)", ChapterPublication
   ) 

web.template.Template.globals['render'] = render 
web.template.Template.globals['rel_uri'] = get_relative_uri 
web.template.Template.globals['markdown'] = markdown2.markdown
web.template.Template.globals['sorted'] = sorted 

app = web.application(urls, globals())
atexit.register(lambda: graph.close()) 

if __name__ == "__main__":
    app.run()
