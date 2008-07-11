import feedparser
from rdflib import ConjunctiveGraph, URIRef, Namespace, Literal
import urlparse
from datetime import date, datetime
import calendar


"""
Maintains an Atom or RSS feed of bookmark links as 
more normalized RDF.

Process:

1. open RDF file into Graph
2. open feed
3. iterate through feed, creating relevant RDFAlchemy objects
4. save graph to file
"""
g = ConjunctiveGraph()

DC = Namespace('http://purl.org/dc/terms/')
BIBO = Namespace('http://purl.org/ontology/bibo/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
EVENT = Namespace('http://purl.org/NET/c4dm/event.owl#')
PO = Namespace('http://purl.org/ontology/po/')
ABM = Namespace('http://www.w3.org/2002/01/bookmark#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

bookmarks_file = 'bookmarks.n3'

def load_graph(graph=g):
    print "loading graph ..."
    graph.parse(bookmarks_file, format='n3')

def save_graph(graph=g):
    print "saving graph ..."
    graph.serialize(bookmarks_file, format='n3') 

mf = "http://ma.gnolia.com/rss/full/people/bdarcus"

mg = feedparser.parse(mf)

def slugify(link):
    urlparse.urlsplit(link)[2]

periodicals = {
       "http://www.csmonitor.com":"Christian Science Monitor", 
       "http://www.bbc.co.uk":"BBC", 
       "http://www.washingtonpost.com":"Washington Post", 
       "http://www.nytimes.com":"New York Times"
       }

def base_uri(link):
   return 'http://' + urlparse.urlsplit(link)[1]

def get_type(link):
    if periodicals.has_key(base_uri(link)):
        return BIBO['Article']
    else:
        return BIBO['Document']

def get_pubtitle(link):
    base = base_uri(link)
    if periodicals.has_key(base):
        return periodicals[base]
    else:
        None

def normalize_date(raw_date):
    utcdt = datetime.utcfromtimestamp(calendar.timegm(raw_date))
    return utcdt.strftime("%Y-%m-%dT%H:%M:%SZ")

def make_pub_triples(link):
    if get_pubtitle(link):
        g.add((URIRef(link), DC['isPartOf'], URIRef(base_uri(link))))
        g.add((URIRef(base_uri(link)), DC['title'], Literal(get_pubtitle(link))))

def items_to_rdf(feed=mg):
    print "parsing feeds ..."
    me = URIRef('http://bruce.darcus.name/about#me')
    for item in feed.entries:
        print item.id
        bookmark_uri = URIRef(item.id)
        # create triples for bookmark
        g.add((bookmark_uri, DC['creator'], me))
        g.add((bookmark_uri, RDF['type'], ABM['Bookmark']))
        g.add((bookmark_uri, DC['modified'], Literal(normalize_date(item.updated_parsed))))
        # create triples for linked document
        clean_link = item.link.split('?')[0]
        doc_uri = URIRef(clean_link)
        g.add((doc_uri, DC['title'], Literal(item.title)))
        make_pub_triples(clean_link)
        type = get_type(clean_link)
        g.add((doc_uri, RDF['type'], type))
        # link bookmark and document
        g.add((bookmark_uri, ABM['recalls'], doc_uri))
    print "created ", len(g), " triples."

load_graph()
items_to_rdf()
save_graph()
