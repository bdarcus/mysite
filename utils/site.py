#!/usr/bin/env python
from rdflib import ConjunctiveGraph, Namespace, Literal, URIRef
from rdflib.Graph import Graph
import urlparse
import web

def get_relative_uri(uri):
    parsed = urlparse.urlsplit(uri)
    if parsed[1] == 'bruce.darcus.name':
        return unicode(parsed[2])
    else:
        return uri

def get_context(identifier):
    """Return a context graph for the given URI identifier"""
    return Graph(identifier=URIRef(identifier))

def get_mime_type(accept_override=None):
    # take into account override that allows a client to request
    # a specific representation, bypassing content negotiation
    if accept_override == '.html': return 'text/html'
    elif accept_override == '.rdf': return 'application/rdf+xml'
    elif accept_override == '.json': return 'application/json'
    elif accept_override == '.n3': return 'text/n3'
   
    # do content negotiation
    accept = Accept('Accept', web.ctx.environ.get('HTTP_ACCEPT', 'text/html'))
    mime_type = accept.best_match(['application/rdf+xml', 'text/n3',
        'application/json', 'text/xml', 'application/xhtml+xml'])
    if mime_type == None:
        mime_type = "text/html"
    return mime_type

def set_html_content_type():
    """IE 6/7 doesn't understand xhtml MIME type
    """
    user_agent = web.ctx.environ.get('HTTP_USER_AGENT', '')
    if 'MSIE 6.0' in user_agent or 'MSIE 7.0' in user_agent:
        web.header('Content-type', 'text/html; charset=UTF-8')
    else:
        web.header('Content-type', 'application/xhtml+xml; charset=UTF-8')

def to_rdf(resource, format='xml'):
    sg = Graph()
    return(sg.serialize(format=format))



