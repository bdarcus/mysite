#!/usr/bin/env python
from optparse import OptionParser
from rdflib.Graph import ConjunctiveGraph
from rdflib.URIRef import URIRef
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib import plugin
from rdflib import URIRef
import sys, os
from sys import exit, exc_info
from datetime import datetime, date
from os.path import dirname, join, split, splitext, expanduser
from unicodedata import normalize

if __name__ == '__main__':
   opt_parser = OptionParser()
   opt_parser.set_usage("usage: load_store.py file1 [file2]")
   files = opt_parser.parse_args()

   # need to have some input files
   if len(files) == 0:
       print opt_parser.usage
       exit

   # load config file
   try:
       config_file = os.path.join(os.path.dirname(__file__), '../config.py')
       config = eval(open(config_file).read())
   except IOError, (errno, strerror):
       print "I/O error(%s): %s" % (errno, strerror)
   except ValueError:
       print "Could not convert data to an integer."
   except:
       print "Unexpected error:", sys.exc_info()[0]
       raise

   DEFAULT_FORMAT_MAP = {
       'rdf': 'xml',
       'rdfs': 'xml',
       'owl': 'xml',
       'n3': 'n3',
       'ttl': 'n3',
       'nt': 'nt',
       'trix': 'trix',
       'xhtml': 'rdfa',
       'html': 'rdfa',
       }

   def get_ext(fpath, lower=True):
       ext = splitext(fpath)[-1]
       if lower:
           ext = ext.lower()
       if ext.startswith('.'):
           ext = ext[1:]
           return ext


   def get_format(fpath, fmap=None):
       fmap = fmap or DEFAULT_FORMAT_MAP
       return fmap.get(get_ext(fpath))


   def strip_extension(fname):
       return fname.split('.')[-2]

   def context_uri(fpath, baseuri=config['rdfalchemy.identifier']):
       fname = split(fpath)[1]
       return baseuri + strip_extension(fname)

   fl = [
       '/Users/darcusb/myweb/meta/about.n3',
       '/Users/darcusb/myweb/meta/publications.n3',
       '/Users/darcusb/myweb/meta/links.n3',
       '/Users/darcusb/myweb/meta/notes.n3',
       '/Users/darcusb/myweb/meta/events.n3'
       ]

   def load_store(files):
       """
       Takes a directory of RDf files and loads them into the store.
       """
       try:
           store = plugin.get('MySQL', Store)('rdflib_db')
           store.open(config['rdflib.config'])
           graph = ConjunctiveGraph(store)
           # iterate through files and load them into the graph
           for fpath in fl:
               graph.parse(fpath, format=get_format(fpath), publicID=context_uri(fpath))
               print fpath + " loaded."
           # save triples to store
           graph.commit()
           graph.close()
       except:
           print "=== error opening RDF store ==="
           exit
       
   load_store(files)
