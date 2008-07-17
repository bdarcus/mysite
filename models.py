#!/usr/bin/env python
# encoding: utf-8

"""
This provides basic object mapping for key classes and relations in the 
Bibliographic Ontology (bibo). Examples:

>>> book = Book('<http://example.net/books/1>')
>>> book.date = "2001"
>>> publisher = Organization('<http://abcbooks.com>')
>>> publisher.name = "ABC Books"
>>> publisher.city = "New York"
>>> book.title = "Some Book Title"
>>> book.publisher = publisher
>>> print(book.publisher.name)
... ABC Books
"""

from rdflib import Namespace
import urlparse
from rdfalchemy import rdfSubject, rdfsSubject, rdfSingle, rdfMultiple
from rdfalchemy.orm import mapper
import sha

DC = Namespace('http://purl.org/dc/terms/')
BIBO = Namespace('http://purl.org/ontology/bibo/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
EVENT = Namespace('http://purl.org/NET/c4dm/event.owl#')
PO = Namespace('http://purl.org/ontology/po/')
BM = Namespace('http://www.w3.org/2002/01/bookmark#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
BIO = Namespace('http://purl.org/vocab/bio/0.1/')
GEONAMES = Namespace('http://www.geonames.org/ontology#')
SIOCT = Namespace('http://rdfs.org/sioc/types#')

class Category(rdfSubject):
    rdf_type = SIOCT['Category']
    pref_label = rdfSingle(SKOS.prefLabel)

class Bookmark(rdfSubject):
    rdf_type = BM['Bookmark']
    recalls = rdfSingle(BM.recalls, range_type=BIBO.Document)
    modified = rdfSingle(DC.modified)
    short_description = rdfSingle(BIBO.shortDescription)
    creator = rdfSingle(DC.creator)

    @property
    def container_title(self):
        doc = self.recalls
        if BIBO.Article == doc[RDF.type]:
            return doc.periodical.title
        elif doc.container:
            return doc.container.title
        else:
            return None
        
    def __cmp__(self, other):
        """
        By default, we sort a list of Bookmark objects in reverse date modified order
        """
        return cmp(other.modified, self.modified)


class Document(rdfSubject):
    rdf_type = BIBO.Document
    # to avoid clash with rdflib's Namespace class, have to tweak syntax on title
    title = rdfSingle(DC['title'])
    alt_titles = rdfMultiple(DC.alt)
    date = rdfSingle(DC.date)
    issued = rdfSingle(DC.issued)
    container = rdfSingle(DC.isPartOf, range_type=BIBO.Collection)
    modified = rdfSingle(DC.modified)
    description = rdfSingle(DC.description)
    abstract = rdfSingle(DC['abstract'])
    creators = rdfMultiple(DC.creator, range_type=FOAF.Person)
    formats = rdfMultiple(DC.hasFormat)
    authorList = rdfMultiple(BIBO.authorList)
    subjects = rdfMultiple(DC.subject, range_type=SKOS.Concept)
    content = rdfSingle(BIBO.content)
    
    def __cmp__(self, other):
        """
        By default, we sort a list of Document objects in reverse date order
        """
        return cmp(((other.date or other.issued), self.title), ((self.date or self.issued), other.title))


class Collection(rdfSubject):
    rdf_type = BIBO.Collection
    title = rdfSingle(DC['title'])
    publisher = rdfSingle(DC.publisher,range_type=FOAF.Organization)

class Series(Collection):
    rdf_type = BIBO.Series

class Article(Document):
    rdf_type = BIBO.Article
    volume = rdfSingle(BIBO.volume)
    issue = rdfSingle(BIBO.issue)
    pages = rdfSingle(BIBO.pages)
    page_start = rdfSingle(BIBO.pageStart)
    page_end = rdfSingle(BIBO.pageEnd)
    periodical = rdfSingle(DC.isPartOf, range_type=BIBO.Periodical)

class AcademicArticle(Article):
    rdf_type = BIBO.AcademicArticle
    peer_reviewed = rdfSingle(BIBO.peerReviewed)
    doi = rdfSingle(BIBO.doi)

class Periodical(rdfSubject):
    rdf_type = BIBO.Periodical
    title = rdfSingle(DC['title'])
    issn = BIBO.issn
    publisher = rdfSingle(DC.publisher,range_type=FOAF.Organization)

class Journal(Periodical):
    rdf_type = BIBO.Journal

class Chapter(Document):
    rdf_type = BIBO.Chapter
    # a book can be tied to either a standalone Book, or an EditedBook
    book = rdfSingle(DC.isPartOf, range_type=BIBO.Book)
    edited_book = rdfSingle(DC.isPartOf, range_type=BIBO.EditedBook)
    chapter = rdfSingle(BIBO.chapter)

    # need to be able to sort by chapter number


    @property
    # is chapter part of an edited collection, or of a complete book?
    # NOT WORKING
    def standalone(self):
        if len(self.edited_book.editors) > 0:
            return True
        else:
            return False

class Review(Article):
    # reviewed resource
    rdf_type = BIBO.Review
    review_of = rdfSingle(BIBO.reviewOf)

class Note(Document):
    rdf_type = BIBO.Note

class Image(Document):
    rdf_type = BIBO.Image
    
class Book(Document):
    rdf_type = BIBO.Book
    publisher = rdfSingle(DC.publisher,range_type=FOAF.Organization)
    series = rdfSingle(DC.isPartOf, range_type=BIBO.Series)

class EditedBook(Book):
    rdf_type = BIBO.EditedBook
    editors = rdfMultiple(BIBO.editorList, range_type=FOAF.Person)

class Transcript(Document):
    rdf_type = BIBO.Transcript
    transcript_of = rdfSingle(BIBO.transcriptOf, range_type=BIBO.Interview)

class Event(rdfSubject):
    rdf_type = EVENT.Event
    date = rdfSingle(DC.date)
    description = rdfSingle(DC.description)

    def slug(self):
        return ('').join(urlparse.urlsplit(self.resUri)[2:])

class Interview(Event):
    rdf_type = BIBO.Interview
    interviewer = rdfMultiple(BIBO.interviewer, range_type=FOAF.Person)
    interviewee = rdfMultiple(BIBO.interviewee, range_type=FOAF.Person)
    broadcasts = rdfMultiple(BIBO.broadcast, range_type=PO.Broadcast)
    transcript = rdfSingle(BIBO.transcript, range_type=BIBO.Transcript)

# PO

class Broadcast(Event):
    rdf_type = PO.Broadcast
    broadcast_of = rdfSingle(PO.broadcast_of, range_type=PO.Episode)

# might subclass an AudioVisualDocument?
class Episode(rdfSubject):
    rdf_type = PO.Episode
    part_of = rdfSingle(DC.isPartOf, range_type=PO.Programme)

class Programme(rdfSubject):
    rdf_type = PO.Programme

# FOAF

class Agent(rdfSubject):
    """
    generates a hashed email address
    """
    def gen_mbox_sha1sum(mbox):
        return sha.sha(mbox).hexdigest()

    rdf_type = FOAF.Agent
    name = rdfSingle(FOAF.name)
    depiction = rdfSingle(FOAF.depiction)
    description = rdfSingle(DC.description)
    openid = rdfSingle(FOAF.openid) 
    mbox = rdfSingle(FOAF.mbox)
    mbox_sha1sum = gen_mbox_sha1sum(str(mbox))
    based_near = rdfSingle(FOAF.based_near, range_type=GEONAMES.Feature)

class Person(Agent):
    rdf_type = FOAF.Person
    interests = rdfMultiple(FOAF.interest, range_type=SKOS.Concept)
    bio = rdfSingle(BIO.olb)

class Organization(Agent):
    rdf_type = FOAF.Organization

# SKOS

class Concept(rdfSubject):
    rdf_type = SKOS.Concept
    pref_label = rdfSingle(SKOS.prefLabel)
    alt_labels = rdfMultiple(SKOS.altLabel)
    broader = rdfMultiple(SKOS.broader)
    narrower = rdfMultiple(SKOS.narrower)
    related = rdfMultiple(SKOS.related)
    editorial_notes = rdfMultiple(SKOS.editorialNote)
    scope_notes = rdfMultiple(SKOS.scopeNote)

    def __cmp__(self, other):
        return cmp(self.pref_label, other.pref_label)

    def slug(self):
        return ('').join(urlparse.urlsplit(self.resUri)[2:])


class Place(rdfSubject):
    rdf_type = GEONAMES.Feature
    name = rdfSingle(GEONAMES.name)


mapper()
